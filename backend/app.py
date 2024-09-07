from fastapi import FastAPI, HTTPException, Request, Depends, status
import pandas as pd
import together
from datetime import timedelta
from data_models import (
    ThemeExtractionRequest,
    SimilarItemsRequest,
    UserRegistrationRequest,
)
from cors_settings import app
from security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    TokenData,
    register_user,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from rate_limiter import rate_limit_user
import os
import logging

from utils.env_loader import load_environment_variables
from utils.clients import initialize_clients
from utils.dataset_loader import dataset_loader

hf_token = load_environment_variables()

qdrant_client, encoder = initialize_clients()


def load_csv_data():
    return pd.read_csv("../processor/files/filteredItemsData.csv")


@app.post("/register", response_description="User added into the database")
async def create_user(user: UserRegistrationRequest, request: Request):
    await rate_limit_user(request)
    user_dict = user.dict()
    new_user = await register_user(user_dict)
    return JSONResponse(content=new_user, status_code=201)


@app.post("/token")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    await rate_limit_user(request)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=3600)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "user")},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/check_login")
async def check_login(request: Request, current_user: TokenData = Depends(get_current_active_user)):
    await rate_limit_user(request, username=current_user.username)
    return {"message": "Logged in"}


@app.post("/extract_themes/")
async def extract_themes(
    request: ThemeExtractionRequest,
    http_request: Request,
    current_user: TokenData = Depends(get_current_active_user),
):
    await rate_limit_user(http_request, username=current_user.username)

    together.api_key = os.getenv("TOGETHER_AI_API_KEY")

    nsfw_prompt = f"""
instruction: Given the user prompt below, determine if it contains any not safe for work (NSFW) content such as explicit violence, gore, nudity, or sexual themes. Respond with "NSFW" if the description contains such content, otherwise respond with "SFW".

user input: {request.user_input}

output:"""
    nsfw_output = together.Complete.create(
        prompt=nsfw_prompt,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=10,
    )
    nsfw_result = nsfw_output["output"]["choices"][0]["text"].strip()

    if nsfw_result == "NSFW":
        raise HTTPException(status_code=400, detail="NSFW content detected")

    prompt = f"""
instruction: Take a detailed description of a Counter-Strike: Global Offensive (CS:GO) item and summarize the key elements such as the type of item (e.g., weapon skin, knife, sticker), the general theme (e.g., futuristic, vintage, militaristic), main colors, and any specific patterns or symbols. If the description is brief or vague, use your best judgment to infer the theme, main colors, or key features. Follow any specific color or theme preferences mentioned in the prompt as closely as possible. Keep your output concise and to the point.

Example 1:
Description: "A CS:GO loadout theme featuring neon designs, electric blue and bright pink colors, and lightning bolt patterns."
Output: neon theme, electric blue, bright pink, lightning bolts

Example 2:
Description: "A stealth-themed CS:GO skin with a camouflage pattern in green, brown, and black."
Output: stealth theme, camouflage pattern, green, brown, black

Example 3:
Description: "A weapon skin inspired by ancient mythology, with gold, bronze, and aged patina colors, depicting legendary creatures and cryptic symbols."
Output: Weapon skin, ancient mythology theme, gold, bronze, aged patina, legendary creatures, cryptic symbols

Example (simplified):
Description: "A full pink, cute and girly themed CS:GO loadout."
Output: pink, cute and girly theme

user input: {request.user_input}

output:"""
    try:
        output = together.Complete.create(
            prompt=prompt,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=1000,
        )
        result = output["output"]["choices"][0]["text"].strip()
        result = result.replace("CS:GO", "Counter-Strike")
        themes = [theme.strip() for theme in result.split(",")]
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.post("/find_similar_items/")
async def find_similar_items(
    request: SimilarItemsRequest,
    current_user: TokenData = Depends(get_current_active_user),
    http_request: Request = None,
):
    await rate_limit_user(http_request, username=current_user.username)

    text_input = request.text_input
    query_vector = encoder.encode(text_input).tolist()

    hf_dataset = dataset_loader(hf_token)
    unique_weapon_types = list(set(hf_dataset["train"]["weapon_type"]))

    results = {}
    for weapon_type in unique_weapon_types:
        logging.debug(f"Querying weapon type: {weapon_type}")

        hits = qdrant_client.search(
            collection_name=os.getenv("COLLECTION_NAME"),
            query_vector=query_vector,
            limit=10,
            query_filter={"must": [{"key": "weapon_type", "match": {"value": weapon_type}}]},
        )

        logging.debug(f"Hits for {weapon_type}: {hits}")

        filtered_hits = [hit for hit in hits if "StatTrak" not in hit.payload["image_name"] and "Souvenir" not in hit.payload["image_name"]]

        results[weapon_type] = []
        for hit in filtered_hits[:5]:
            results[weapon_type].append({"name": hit.payload["image_name"], "similarity": hit.score})

    return {"items": results}
