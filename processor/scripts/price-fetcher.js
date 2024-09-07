const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const fs = require('fs');

async function fetchData() {
  const url = 'https://csgobackpack.net/api/GetItemsList/v2/';
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    const itemsData = {
      success: data.success,
      currency: data.currency,
      timestamp: data.timestamp,
      items_list: {}
    };
    Object.entries(data.items_list).forEach(([key, value]) => {
        // Initialize default structure for price data to avoid undefined errors
        const defaultPriceData = { Average: 0, Median: 0, Sold: 0 };
      
        // Helper function to safely extract price data
        const getPriceData = (priceObj, period) => {
          return priceObj && priceObj[period] ? {
            Average: priceObj[period].average || 0,
            Median: priceObj[period].median || 0,
            Sold: priceObj[period].sold || 0
          } : defaultPriceData;
        };
      
        // Extract price data safely for each period
        const price24Hours = getPriceData(value.price, "24_hours");
        const price7Days = getPriceData(value.price, "7_days");
        const price30Days = getPriceData(value.price, "30_days");
        const priceAllTime = getPriceData(value.price, "all_time");
      
        itemsData.items_list[key] = {
          Name: value.name,
          Marketable: value.marketable,
          Tradable: value.tradable,
          ClassID: value.classid,
          IconURL: value.icon_url,
          Rarity: value.rarity,
          RarityColor: value.rarity_color,
          Price: {
            "24_hours": price24Hours,
            "7_days": price7Days,
            "30_days": price30Days,
            "All_time": priceAllTime
          }
        };
      });
    fs.writeFile('itemsData.json', JSON.stringify(itemsData, null, 2), (err) => {
      if (err) throw err;
      console.log('Data has been written to file');
    });
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
}

fetchData();