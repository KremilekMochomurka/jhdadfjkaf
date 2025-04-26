const express = require('express');
const router = express.Router();
const braveSearchService = require('../services/braveSearchService');
const apiLimiter = require('../middleware/rateLimit');

/**
 * @route   GET /api/search
 * @desc    Search the web using Brave Search API
 * @access  Public (with rate limiting)
 */
router.get('/search', apiLimiter, async (req, res) => {
  try {
    const result = await braveSearchService.webSearch(req.query);
    res.json(result);
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        error: true,
        message: error.response.data.message || 'Error from Brave Search API',
        code: error.response.status
      });
    }
    res.status(500).json({ error: true, message: 'Server error', details: error.message });
  }
});

/**
 * @route   GET /api/locations
 * @desc    Get information about specific locations
 * @access  Public (with rate limiting)
 */
router.get('/locations', apiLimiter, async (req, res) => {
  try {
    const { ids } = req.query;
    
    if (!ids) {
      return res.status(400).json({ error: true, message: 'Location IDs are required' });
    }
    
    // Convert single ID to array if needed
    const idArray = Array.isArray(ids) ? ids : [ids];
    
    const result = await braveSearchService.getLocationInfo(idArray);
    res.json(result);
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        error: true,
        message: error.response.data.message || 'Error from Brave Location API',
        code: error.response.status
      });
    }
    res.status(500).json({ error: true, message: 'Server error', details: error.message });
  }
});

/**
 * @route   GET /api/location-descriptions
 * @desc    Get AI-generated descriptions for locations
 * @access  Public (with rate limiting)
 */
router.get('/location-descriptions', apiLimiter, async (req, res) => {
  try {
    const { ids } = req.query;
    
    if (!ids) {
      return res.status(400).json({ error: true, message: 'Location IDs are required' });
    }
    
    // Convert single ID to array if needed
    const idArray = Array.isArray(ids) ? ids : [ids];
    
    const result = await braveSearchService.getLocationDescriptions(idArray);
    res.json(result);
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        error: true,
        message: error.response.data.message || 'Error from Brave Location Descriptions API',
        code: error.response.status
      });
    }
    res.status(500).json({ error: true, message: 'Server error', details: error.message });
  }
});

/**
 * @route   GET /api/suggest
 * @desc    Get search suggestions
 * @access  Public (with rate limiting)
 */
router.get('/suggest', apiLimiter, async (req, res) => {
  try {
    const result = await braveSearchService.getSuggestions(req.query);
    res.json(result);
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({
        error: true,
        message: error.response.data.message || 'Error from Brave Suggest API',
        code: error.response.status
      });
    }
    res.status(500).json({ error: true, message: 'Server error', details: error.message });
  }
});

module.exports = router;
