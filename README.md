# Brave Search MCP Server

A Meta Content Provider (MCP) server that acts as a proxy for the Brave Search API.

## Features

- Web search endpoint
- Location information endpoint
- Location descriptions endpoint
- Search suggestions endpoint
- Rate limiting to stay within API limits
- Error handling and logging

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn

## Installation

1. Clone this repository
2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the root directory with the following variables:

```
PORT=3000
BRAVE_SEARCH_API_KEY=your_api_key_here
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=60
```

## Usage

### Start the server

```bash
npm start
```

For development with auto-restart:

```bash
npm run dev
```

### API Endpoints

#### Web Search

```
GET /api/search?q=your+search+query
```

Query parameters:
- `q`: Search query (required)
- `count`: Number of results (optional, default: 10)
- `offset`: Result offset for pagination (optional)
- `country`: Country code (optional)
- `language`: Language code (optional)

#### Location Information

```
GET /api/locations?ids=location_id1&ids=location_id2
```

Query parameters:
- `ids`: Location IDs (required, can be repeated for multiple IDs)

#### Location Descriptions

```
GET /api/location-descriptions?ids=location_id1&ids=location_id2
```

Query parameters:
- `ids`: Location IDs (required, can be repeated for multiple IDs)

#### Search Suggestions

```
GET /api/suggest?q=partial+query
```

Query parameters:
- `q`: Partial search query (required)
- `country`: Country code (optional)
- `language`: Language code (optional)

## Rate Limiting

The server implements rate limiting to stay within the Brave Search API limits:
- Free tier: 1 query/second, 2,000 queries/month

## License

MIT
