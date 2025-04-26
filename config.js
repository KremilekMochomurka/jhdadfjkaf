require('dotenv').config();

module.exports = {
  port: process.env.PORT || 3000,
  braveSearchApiKey: process.env.BRAVE_SEARCH_API_KEY,
  braveSearchApiUrl: 'https://api.search.brave.com/res/v1',
  rateLimitWindowMs: process.env.RATE_LIMIT_WINDOW_MS || 60000, // 1 minute
  rateLimitMaxRequests: process.env.RATE_LIMIT_MAX_REQUESTS || 60 // 60 requests per minute
};
