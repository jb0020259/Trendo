const { google } = require('googleapis');
const { JWT } = require('google-auth-library');

// Initialize the Google Trends API client
const auth = new JWT({
  email: process.env.GOOGLE_CLIENT_EMAIL,
  key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
  scopes: ['https://www.googleapis.com/auth/trends.readonly'],
});

const trends = google.trends({ version: 'v1', auth });

exports.handler = async function(event, context) {
  try {
    // Define the search terms
    const searchTerms = [
      'buy gold',
      'bitcoin investment',
      'stock market investment',
      'real estate investment'
    ];

    // Get the current date and date 30 days ago
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);

    // Format dates for the API
    const formattedStartDate = startDate.toISOString().split('T')[0];
    const formattedEndDate = endDate.toISOString().split('T')[0];

    // Fetch data for each search term
    const results = await Promise.all(
      searchTerms.map(async (term) => {
        const response = await trends.interestOverTime({
          keyword: term,
          startTime: formattedStartDate,
          endTime: formattedEndDate,
          geo: 'US'
        });

        const data = response.data;
        const dates = data.timelineData.map(item => item.time);
        const values = data.timelineData.map(item => item.value[0]);

        return {
          term,
          dates,
          values
        };
      })
    );

    // Format the response
    const formattedResults = {};
    results.forEach(result => {
      formattedResults[result.term] = {
        dates: result.dates,
        values: result.values
      };
    });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify(formattedResults)
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch trend data' })
    };
  }
}; 