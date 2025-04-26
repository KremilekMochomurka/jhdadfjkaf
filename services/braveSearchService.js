const axios = require('axios');
const config = require('../config');

class BraveSearchService {
  constructor() {
    this.apiKey = config.braveSearchApiKey;
    this.baseUrl = config.braveSearchApiUrl;
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': this.apiKey
      }
    });
  }

  /**
   * Perform a web search using Brave Search API
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Search results
   */
  async webSearch(params) {
    try {
      const response = await this.client.get('/web/search', { params });
      return response.data;
    } catch (error) {
      console.error('Error in Brave Search API:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get information about specific locations
   * @param {Array<string>} ids - Location IDs
   * @returns {Promise<Object>} - Location information
   */
  async getLocationInfo(ids) {
    try {
      const params = { ids };
      const response = await this.client.get('/local/pois', { params });
      return response.data;
    } catch (error) {
      console.error('Error in Brave Location API:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get AI-generated descriptions for locations
   * @param {Array<string>} ids - Location IDs
   * @returns {Promise<Object>} - Location descriptions
   */
  async getLocationDescriptions(ids) {
    try {
      const params = { ids };
      const response = await this.client.get('/local/descriptions', { params });
      return response.data;
    } catch (error) {
      console.error('Error in Brave Location Descriptions API:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get search suggestions
   * @param {Object} params - Suggestion parameters
   * @returns {Promise<Object>} - Suggestion results
   */
  async getSuggestions(params) {
    try {
      const response = await this.client.get('/suggest', { params });
      return response.data;
    } catch (error) {
      console.error('Error in Brave Suggest API:', error.response?.data || error.message);
      throw error;
    }
  }
}

module.exports = new BraveSearchService();
