import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/flights/";

// Flight search function
export async function searchFlights(params) {
  try {
    // Backend API call
    const response = await axios.get(`${API_BASE_URL}search/`, {
      params: params
    });
    
    // Process normal response
    if (response.data && response.data.status === true) {
      const flightData = response.data.data;
      
      // Check response structure
      if (flightData && flightData.itineraries && Array.isArray(flightData.itineraries)) {
        // itineraries format response (one-way or round-trip search)
        return {
          data: {
            responseType: "itineraries",
            itineraries: flightData.itineraries,
            token: flightData.token || flightData.flightsSessionId || ""
          }
        };
      } 
      // countryDestination format response (destination search results - everywhere search)
      else if (flightData && flightData.countryDestination) {
        // Return countryDestination data as is (no conversion)
        return {
          data: {
            responseType: "countryDestination",
            countryDestination: flightData.countryDestination,
            token: flightData.countryDestination.context?.sessionId || ""
          }
        };
      } else {
        return { 
          data: {
            responseType: "unknown",
            rawData: flightData
          }
        };
      }
    } else {
      return { 
        data: { 
          responseType: "error",
          error: response.data.message || "Flight search failed" 
        } 
      };
    }
  } catch (error) {
    return { 
      data: { 
        responseType: "error",
        error: error.response?.data?.message || error.message || "Flight search error occurred" 
      } 
    };
  }
}

// Airport autocomplete search function
export async function searchAirports(query) {
  try {
    if (!query || query.trim() === '') {
      return [];
    }
    
    const response = await axios.get(`${API_BASE_URL}get-airports/`, {
      params: { query }
    });

    // Return response data as is
    return response.data || []; 
  } catch (error) {
    return [];
  }
}

// Flight details function
export async function getFlightDetails(token, itineraryId, options = {}) {
  try {
    // Check required parameters
    if (!token || !itineraryId) {
      return {
        status: false,
        message: "Required parameters are missing.",
        data: null
      };
    }
    
    // API call parameters
    const params = {
      token: token,
      itineraryId: itineraryId,
      // Optional parameters
      market: options.market || 'US',
      locale: options.locale || 'en-US',
      currency: options.currency || 'USD',
      // cookie parameter (captcha error prevention, only if provided)
      ...(options.cookie ? { cookie: options.cookie } : {})
    };
    
    // API call
    const response = await axios.get(`${API_BASE_URL}get-flight-details/`, { params });
    
    // Check response data
    if (response.data && response.data.status === true && response.data.data) {
      // Return response as is (original structure)
      return response.data;
    } else {
      return {
        status: false,
        message: response.data.message || "Failed to load flight details",
        data: null
      };
    }
  } catch (error) {
    // Generate detailed error message
    let errorMessage = "Failed to load flight details";
    if (error.response) {
      errorMessage = error.response.data?.message || 
                     `Server error (${error.response.status}): ${error.response.statusText}`;
    } else if (error.request) {
      errorMessage = "Failed to connect to server. Please check your network connection.";
    } else {
      errorMessage = error.message || errorMessage;
    }
    
    return {
      status: false,
      message: errorMessage,
      data: null
    };
  }
}

// Search history retrieval function (requires login)
export async function getSearchHistory() {
  try {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      return { error: "Login required" };
    }
    
    const response = await axios.get(`${API_BASE_URL}get-search-history/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      return { error: "Login required" };
    }
    return { results: [] };
  }
}

// Get complete search results function
export async function getCompleteResults(sessionId, options = {}) {
  try {
    if (!sessionId || sessionId.trim() === '') {
      console.error('getCompleteResults called with empty sessionId');
      return { 
        data: { 
          responseType: "error",
          error: "Session ID is empty or invalid" 
        } 
      };
    }
    
    console.log(`Calling API with sessionId: ${sessionId}`);
    
    // Request parameter configuration
    const params = {
      sessionId: sessionId,
      ...options
    };
    
    const apiUrl = `${API_BASE_URL}get-complete-results/`;
    console.log(`Making API call to: ${apiUrl} with params:`, params);
    
    // Backend API call
    const response = await axios.get(apiUrl, {
      params: params
    });
    
    console.log('Backend raw response:', response);
    console.log('Backend response data:', response.data);
    
    // Process normal response
    if (response.data && response.data.status === true) {
      const data = response.data.data;
      console.log('Data extracted from response:', data);
      
      if (data && data.itineraries && Array.isArray(data.itineraries)) {
        console.log(`Found ${data.itineraries.length} itineraries in response`);
        return {
          data: {
            responseType: "itineraries",
            itineraries: data.itineraries,
            token: data.context?.sessionId || data.flightsSessionId || sessionId
          }
        };
      } else if (data && data.content && data.content.results) {
        // Handle alternative response format
        console.log(`Found alternative format with ${data.content.results.length} results`);
        return {
          data: {
            responseType: "itineraries",
            itineraries: data.content.results,
            token: data.content.context?.sessionId || sessionId
          }
        };
      } else {
        console.warn('Unknown response data structure:', data);
        return { 
          data: {
            responseType: "unknown",
            rawData: data
          }
        };
      }
    } else {
      console.error('API returned error or invalid status:', response.data);
      
      // Check for special error code from backend
      if (response.data && response.data.errorCode === 'API_UNAVAILABLE') {
        console.warn('SkyScanner API is unavailable, using initial search results');
        return {
          data: {
            responseType: "use_initial_results",
            message: "Using initial search results as SkyScanner API is unavailable"
          }
        };
      }
      
      return { 
        data: { 
          responseType: "error",
          error: response.data.message || "Failed to complete flight search" 
        } 
      };
    }
  } catch (error) {
    console.error('API error during getCompleteResults:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    
    // Check for special error code from backend
    if (error.response?.data?.errorCode === 'API_UNAVAILABLE') {
      console.warn('SkyScanner API is unavailable, using initial search results');
      return {
        data: {
          responseType: "use_initial_results",
          message: "Using initial search results as SkyScanner API is unavailable"
        }
      };
    }
    
    return { 
      data: { 
        responseType: "error",
        error: error.response?.data?.message || error.message || "Failed to complete flight search" 
      } 
    };
  }
}

