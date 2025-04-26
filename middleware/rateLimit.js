const rateLimit = require('express-rate-limit');
const config = require('../config');

// Create a rate limiter to stay within Brave Search API limits
// Free tier: 1 query/second, 2,000 queries/month
const apiLimiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  max: config.rateLimitMaxRequests,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    status: 429,
    message: 'Too many requests, please try again later.'
  }
});

module.exports = apiLimiter;
