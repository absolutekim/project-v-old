<template>
  <div class="flight-container">
    <!-- Top banner with gradient instead of image -->
    <div class="banner-container mb-8 rounded-xl overflow-hidden relative max-w-6xl mx-auto">
      <div class="gradient-banner w-full h-64 flex flex-col justify-center items-center px-8 md:px-12 text-center">
        <h1 class="text-4xl md:text-5xl font-bold mb-3 text-white">Flight Search</h1>
        <p class="text-white md:text-2xl max-w-xl font-medium banner-text">Find the best flight to your destination</p>
      </div>
    </div>
    
    <!-- Search form -->
    <div class="search-form p-6 mb-8 max-w-3xl mx-auto">
      <div class="flex justify-center gap-6 mb-5">
        <div class="flex gap-2 items-center">
          <input type="radio" id="round-trip" v-model="tripType" value="round" class="w-5 h-5 accent-primary">
          <label for="round-trip" class="text-lg font-medium">Round Trip</label>
        </div>
        <div class="flex gap-2 items-center">
          <input type="radio" id="one-way" v-model="tripType" value="one-way" class="w-5 h-5 accent-primary">
          <label for="one-way" class="text-lg font-medium">One Way</label>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5 mx-auto">
        <!-- Departure -->
        <div class="relative">
          <label class="block mb-2 font-medium text-gray-700 text-center">Departure</label>
          <div class="relative">
            <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">flight_takeoff</i>
            <input 
              type="text" 
              v-model="originQuery" 
              @input="searchOriginAirports" 
              placeholder="City or Airport" 
              class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30"
            >
          </div>
          <div v-if="showOriginDropdown && originAirports.length" class="dropdown-menu absolute z-10 bg-white w-full mt-1 max-h-64 overflow-y-auto">
            <div 
              v-for="airport in originAirports" 
              :key="airport.presentation.id" 
              @click="selectOrigin(airport)"
              class="dropdown-item p-3 cursor-pointer hover:bg-primary/5"
            >
              <div class="font-medium">{{ airport.presentation.title }}</div>
              <div class="text-sm text-gray-500">{{ airport.presentation.subtitle }}</div>
            </div>
          </div>
        </div>
        
        <!-- Destination -->
        <div class="relative">
          <label class="block mb-2 font-medium text-gray-700 text-center">Destination</label>
          <div class="relative">
            <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">flight_land</i>
            <input 
              type="text" 
              v-model="destinationQuery" 
              @input="searchDestinationAirports" 
              placeholder="City or Airport" 
              class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30"
            >
          </div>
          <div v-if="showDestinationDropdown && destinationAirports.length" class="dropdown-menu absolute z-10 bg-white w-full mt-1 max-h-64 overflow-y-auto">
            <div 
              v-for="airport in destinationAirports" 
              :key="airport.presentation.id" 
              @click="selectDestination(airport)"
              class="dropdown-item p-3 cursor-pointer hover:bg-primary/5"
            >
              <div class="font-medium">{{ airport.presentation.title }}</div>
              <div class="text-sm text-gray-500">{{ airport.presentation.subtitle }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6 mx-auto">
        <!-- Departure date -->
        <div>
          <label class="block mb-2 font-medium text-gray-700 text-center">Departure Date</label>
          <div class="relative">
            <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">event</i>
            <input 
              type="date" 
              v-model="departDate" 
              class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30"
              :min="today"
            >
          </div>
        </div>
        
        <!-- Return date (only for round trips) -->
        <div v-if="tripType === 'round'">
          <label class="block mb-2 font-medium text-gray-700 text-center">Return Date</label>
          <div class="relative">
            <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">event</i>
            <input 
              type="date" 
              v-model="returnDate" 
              class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30"
              :min="departDate || today"
            >
          </div>
        </div>
        
        <!-- Cabin class -->
        <div>
          <label class="block mb-2 font-medium text-gray-700 text-center">Cabin Class</label>
          <div class="relative">
            <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">airline_seat_recline_normal</i>
            <select v-model="cabinClass" class="w-full pl-10 pr-3 py-3 border rounded-lg appearance-none focus:ring focus:ring-primary/30">
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First</option>
            </select>
            <i class="material-icons absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">arrow_drop_down</i>
          </div>
        </div>
        
        <!-- Number of passengers -->
        <div>
          <label class="block mb-2 font-medium text-gray-700 text-center">Passengers</label>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="text-sm text-gray-600 mb-1 block text-center">Adult</label>
              <div class="relative">
                <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">person</i>
                <input type="number" v-model="adults" min="1" max="9" class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30">
              </div>
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block text-center">Child</label>
              <div class="relative">
                <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">child_care</i>
                <input type="number" v-model="children" min="0" max="9" class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30">
              </div>
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block text-center">Infant</label>
              <div class="relative">
                <i class="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-primary">baby_changing_station</i>
                <input type="number" v-model="infants" min="0" max="9" class="w-full pl-10 pr-3 py-3 border rounded-lg focus:ring focus:ring-primary/30">
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <button 
        @click="searchFlights" 
        class="search-button py-4 px-6 rounded-lg font-semibold text-lg flex items-center justify-center mx-auto w-full md:w-64"
        :disabled="isLoading"
      >
        <i class="material-icons mr-2" v-if="!isLoading">search</i>
        <i class="material-icons animate-spin mr-2" v-if="isLoading">sync</i>
        {{ isLoading ? 'Searching...' : 'Search Flights' }}
      </button>
    </div>
    
    <!-- Search results -->
    <div v-if="flightResults && flightResults.data" class="results-container bg-white rounded-lg shadow-md p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-6 flex items-center justify-center">
        <i class="material-icons mr-2 text-primary">flight</i>
        Search Results
      </h2>
      
      <!-- General flight search results (one-way or round-trip) -->
      <div v-if="flightResults.data.responseType === 'itineraries' && flightResults.data.itineraries && flightResults.data.itineraries.length">
        <!-- Summary of search results -->
        <div class="results-summary p-4 rounded-lg mb-5 text-center">
          <div class="flex flex-col md:flex-row justify-center items-center">
            <div class="text-lg font-medium text-gray-700">
              Total <span class="font-bold text-primary">{{ flightResults.data.itineraries.length }}</span> flight search results
            </div>
            <div class="text-sm text-gray-600 ml-4">
              {{ currentPage * itemsPerPage + 1 }}-{{ Math.min((currentPage + 1) * itemsPerPage, flightResults.data.itineraries.length) }}th result
            </div>
          </div>
          
          <!-- API limit notification message -->
          <div v-if="apiLimitReached" class="mt-3 text-sm text-orange-600 flex items-center justify-center">
            <i class="material-icons text-orange-500 mr-1 text-base">info</i>
            현재 Skyscanner API 제한으로 인해 검색 결과가 일부만 제공됩니다. 표시된 항공편 중에서 선택해 주세요.
          </div>
          
          <!-- Flight sorting options -->
          <div class="mt-3 flex flex-wrap gap-3 items-center justify-center">
            <span class="text-sm font-medium text-gray-600">Sort by:</span>
            <button 
              @click="sortFlights('price')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="flightSortOption === 'price' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Lowest Price
            </button>
            <button 
              @click="sortFlights('priceDesc')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="flightSortOption === 'priceDesc' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Highest Price
            </button>
            <button 
              @click="sortFlights('duration')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="flightSortOption === 'duration' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Shortest Duration
            </button>
            <button 
              @click="sortFlights('departure')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="flightSortOption === 'departure' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Fastest Departure
            </button>
          </div>
        </div>
        
        <div v-for="flight in paginatedFlights" :key="flight.id" class="flight-card mb-5 max-w-4xl mx-auto">
          <div class="card-header p-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
              <div class="flex flex-col text-center md:text-left">
                <div class="text-xl font-semibold">
                  {{ getOriginDestinationText(flight) }}
                </div>
                <div class="text-sm text-gray-600 mt-1">
                  {{ getFlightDateInfo(flight) }}
                </div>
              </div>
              <div class="mt-3 md:mt-0">
                <div class="price-tag text-2xl">{{ flight.price?.formatted || 'Price information not available' }}</div>
                <div class="text-sm text-gray-500 text-right">Total Price</div>
              </div>
            </div>
          </div>
          
          <div class="p-4">
            <div v-for="leg in flight.legs" :key="leg.id" class="flight-leg first:border-t-0 first:pt-0 mt-3">
              <div class="flex flex-col md:flex-row justify-between items-center mb-3">
                <div class="text-center md:text-left">
                  <div class="text-lg font-semibold">
                    {{ leg.origin.displayCode }} → {{ leg.destination.displayCode }}
                  </div>
                  <div class="text-sm text-gray-600">
                    {{ formatDate(leg.departure) }} - {{ formatDate(leg.arrival) }}
                    <span v-if="leg.timeDeltaInDays > 0" class="text-orange-500 font-medium ml-1">
                      (+{{ leg.timeDeltaInDays }} days)
                    </span>
                  </div>
                </div>
                <div class="flex flex-col items-center md:items-end mt-2 md:mt-0">
                  <div class="flight-duration">{{ formatDuration(leg.durationInMinutes) }}</div>
                  <div class="text-sm mt-1">
                    <span v-if="leg.stopCount === 0" class="text-green-600 font-medium">Direct</span>
                    <span v-else class="text-orange-500 font-medium">{{ leg.stopCount }} Stop</span>
                  </div>
                </div>
              </div>
              
              <div class="flex flex-wrap gap-3 mt-3 justify-center">
                <div v-for="carrier in leg.carriers.marketing" :key="carrier.id" class="flex items-center carrier-badge px-3 py-2 rounded-full">
                  <span class="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center text-xs mr-2 text-primary">{{ carrier.name?.substring(0,1) || 'A' }}</span>
                  <span class="text-sm font-medium">{{ carrier.name || 'Airline information not available' }}</span>
                </div>
              </div>
            </div>
            
            <div class="mt-4 flex justify-center">
              <button 
                @click="viewFlightDetails(flight)" 
                class="details-button bg-primary text-white py-2.5 px-5 rounded-lg hover:bg-primary-dark transition flex items-center"
              >
                <span class="mr-1">Details</span>
                <i class="material-icons text-sm">arrow_forward</i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Pagination control -->
        <div v-if="totalPages > 1" class="flex justify-center mt-8 mb-4 items-center">
          <button 
            @click="currentPage = 0" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="currentPage === 0"
            :class="{'opacity-50 cursor-not-allowed': currentPage === 0}"
          >
            <i class="material-icons text-sm">first_page</i>
          </button>
          
          <button 
            @click="currentPage--" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="currentPage === 0"
            :class="{'opacity-50 cursor-not-allowed': currentPage === 0}"
          >
            <i class="material-icons text-sm">chevron_left</i>
          </button>
          
          <div class="flex mx-2">
            <template v-for="page in pageNumbers" :key="page">
              <button 
                @click="currentPage = page" 
                class="pagination-button mx-1 px-4 py-2 rounded-lg"
                :class="page === currentPage ? 'bg-primary text-white' : 'border hover:bg-gray-100'"
              >
                {{ page + 1 }}
              </button>
            </template>
          </div>
          
          <button 
            @click="currentPage++" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="currentPage >= totalPages - 1"
            :class="{'opacity-50 cursor-not-allowed': currentPage >= totalPages - 1}"
          >
            <i class="material-icons text-sm">chevron_right</i>
          </button>
          
          <button 
            @click="currentPage = totalPages - 1" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="currentPage >= totalPages - 1"
            :class="{'opacity-50 cursor-not-allowed': currentPage >= totalPages - 1}"
          >
            <i class="material-icons text-sm">last_page</i>
          </button>
        </div>
      </div>
      
      <!-- Destination search results (countryDestination) -->
      <div v-else-if="flightResults.data.responseType === 'countryDestination' && flightResults.data.countryDestination" class="destination-results">
        <!-- Total results count display -->
        <div class="mb-6 p-4 results-summary rounded-lg text-center">
          <div class="flex items-center justify-center">
            <i class="material-icons mr-2 text-primary">travel_explore</i>
            <div class="text-lg font-medium text-gray-700">
              {{ flightResults.data.countryDestination.context.totalResults }} destination search results
            </div>
          </div>
          
          <!-- Sorting options -->
          <div class="mt-3 flex flex-wrap gap-3 items-center justify-center">
            <span class="text-sm font-medium text-gray-600">Sort by:</span>
            <button 
              @click="sortDestinations('price')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="sortOption === 'price' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Lowest Price
            </button>
            <button 
              @click="sortDestinations('priceDesc')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="sortOption === 'priceDesc' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Highest Price
            </button>
            <button 
              @click="sortDestinations('name')" 
              class="sort-button px-3 py-1.5 rounded-full text-sm hover:bg-primary/10 transition"
              :class="sortOption === 'name' ? 'bg-primary/10 text-primary font-medium' : 'bg-white text-gray-600'"
            >
              Name
            </button>
          </div>
          
          <!-- Selected category buttons -->
          <div class="mt-3 flex flex-wrap gap-2 justify-center">
            <button 
              v-for="bucket in flightResults.data.countryDestination.buckets.slice(0, 5)" 
              :key="bucket.id"
              class="category-button px-3 py-1.5 rounded-full border text-sm hover:bg-primary/10 transition"
            >
              {{ bucket.label }}
            </button>
          </div>
        </div>
        
        <!-- Destination card grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          <div 
            v-for="result in paginatedDestinations" 
            :key="result.id"
            class="destination-card overflow-hidden rounded-lg border hover:shadow-lg transition duration-300 bg-white"
          >
            <!-- Destination information -->
            <div class="p-4">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="text-lg font-semibold text-gray-800">
                    {{ result.content?.location?.name || 'Unknown location' }}
                  </h3>
                  <div class="text-sm text-gray-500 mt-1">
                    {{ result.content?.location?.type || '' }}
                    {{ result.content?.location?.iata ? `(${result.content.location.iata})` : '' }}
                  </div>
                </div>
                
                <!-- Price information -->
                <div v-if="result.content?.flightQuotes?.cheapest || result.content?.flightQuotes?.direct" class="flex flex-col items-end">
                  <div class="text-lg font-bold text-primary">
                    {{ result.content.flightQuotes.direct?.price || result.content.flightQuotes.cheapest?.price || 'Price information not available' }}
                  </div>
                  <div class="flex items-center text-xs mt-1">
                    <span 
                      v-if="result.content.flightQuotes.direct?.direct || result.content.flightQuotes.cheapest?.direct" 
                      class="text-green-600 font-medium"
                    >
                      <i class="material-icons text-xs mr-0.5">flight</i> Direct
                    </span>
                    <span v-else class="text-orange-500 font-medium">Stop</span>
                  </div>
                </div>
              </div>
              
              <!-- Hotel price information (if available) -->
              <div v-if="result.content?.hotelQuotes?.standard" class="flex items-center mt-3 pt-3 border-t border-gray-100">
                <i class="material-icons text-gray-400 mr-1 text-sm">hotel</i>
                <span class="text-sm text-gray-500">Hotel average {{ result.content.hotelQuotes.standard.price }} from</span>
              </div>
              
              <!-- Action button -->
              <div class="mt-4 flex justify-end">
                <button 
                  @click="viewDestinationDetails(result)" 
                  class="text-primary font-medium text-sm hover:text-primary-dark transition flex items-center"
                >
                  <span>Details</span>
                  <i class="material-icons text-sm ml-1">arrow_forward</i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination control -->
        <div v-if="totalDestinationPages > 1" class="flex justify-center mt-8 mb-4 items-center">
          <button 
            @click="destinationPage = 0" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="destinationPage === 0"
            :class="{'opacity-50 cursor-not-allowed': destinationPage === 0}"
          >
            <i class="material-icons text-sm">first_page</i>
          </button>
          
          <button 
            @click="destinationPage--" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="destinationPage === 0"
            :class="{'opacity-50 cursor-not-allowed': destinationPage === 0}"
          >
            <i class="material-icons text-sm">chevron_left</i>
          </button>
          
          <div class="flex mx-2">
            <template v-for="page in destinationPageNumbers" :key="page">
              <button 
                @click="destinationPage = page" 
                class="pagination-button mx-1 px-4 py-2 rounded-lg"
                :class="page === destinationPage ? 'bg-primary text-white' : 'border hover:bg-gray-100'"
              >
                {{ page + 1 }}
              </button>
            </template>
          </div>
          
          <button 
            @click="destinationPage++" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="destinationPage >= totalDestinationPages - 1"
            :class="{'opacity-50 cursor-not-allowed': destinationPage >= totalDestinationPages - 1}"
          >
            <i class="material-icons text-sm">chevron_right</i>
          </button>
          
          <button 
            @click="destinationPage = totalDestinationPages - 1" 
            class="pagination-button mx-1 px-3 py-2 rounded-lg border hover:bg-gray-100" 
            :disabled="destinationPage >= totalDestinationPages - 1"
            :class="{'opacity-50 cursor-not-allowed': destinationPage >= totalDestinationPages - 1}"
          >
            <i class="material-icons text-sm">last_page</i>
          </button>
        </div>
      </div>
      
      <!-- Error message -->
      <div v-else-if="flightResults.data.responseType === 'error'" class="text-center p-8 text-red-500 bg-red-50 rounded-lg">
        <i class="material-icons text-4xl mb-2 text-red-400">error</i>
        <p class="text-lg">{{ flightResults.data.error || 'An error occurred during the search.' }}</p>
      </div>
      
      <!-- No search results -->
      <div v-else class="text-center p-8 text-gray-500 bg-gray-50 rounded-lg">
        <i class="material-icons text-4xl mb-2 text-gray-400">search_off</i>
        <p class="text-lg">No search results. Try different search conditions.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { searchAirports, searchFlights as apiSearchFlights, getCompleteResults } from '@/api/flight';

export default {
  name: 'FlightView',
  setup() {
    const router = useRouter();
    
    // Search Form State
    const tripType = ref('round');
    const originQuery = ref('');
    const destinationQuery = ref('');
    const departDate = ref('');
    const returnDate = ref('');
    const cabinClass = ref('economy');
    const adults = ref(1);
    const children = ref(0);
    const infants = ref(0);
    
    // Airport Autocomplete Related State
    const originAirports = ref([]);
    const destinationAirports = ref([]);
    const showOriginDropdown = ref(false);
    const showDestinationDropdown = ref(false);
    const selectedOrigin = ref(null);
    const selectedDestination = ref(null);
    
    // Search Results and Loading State
    const flightResults = ref(null);
    const isLoading = ref(false);
    
    // Pagination related state
    const currentPage = ref(0); // 0-based page number
    const itemsPerPage = ref(50); // Number of items per page
    
    // Flight sorting related state and functions
    const flightSortOption = ref('price'); // Default sorting: lowest price
    
    // Flight sorting function
    const sortFlights = (option) => {
      flightSortOption.value = option;
      currentPage.value = 0; // Go back to the first page when sorting
    };
    
    // Sorted flight list
    const sortedFlights = computed(() => {
      if (!flightResults.value || !flightResults.value.data || !flightResults.value.data.itineraries) {
        return [];
      }
      
      const flights = [...flightResults.value.data.itineraries];
      
      switch (flightSortOption.value) {
        case 'price':
          return flights.sort((a, b) => {
            const priceA = a.price?.raw || Number.MAX_VALUE;
            const priceB = b.price?.raw || Number.MAX_VALUE;
            return priceA - priceB;
          });
        case 'priceDesc':
          return flights.sort((a, b) => {
            const priceA = a.price?.raw || 0;
            const priceB = b.price?.raw || 0;
            return priceB - priceA;
          });
        case 'duration':
          return flights.sort((a, b) => {
            const durationA = a.legs[0]?.durationInMinutes || Number.MAX_VALUE;
            const durationB = b.legs[0]?.durationInMinutes || Number.MAX_VALUE;
            return durationA - durationB;
          });
        case 'departure':
          return flights.sort((a, b) => {
            const dateStrA = a.legs[0]?.departure;
            const dateStrB = b.legs[0]?.departure;
            if (!dateStrA) return 1;
            if (!dateStrB) return -1;
            return new Date(dateStrA) - new Date(dateStrB);
          });
        default:
          return flights;
      }
    });
    
    // Paginated flight list
    const paginatedFlights = computed(() => {
      const start = currentPage.value * itemsPerPage.value;
      const end = start + itemsPerPage.value;
      return sortedFlights.value.slice(start, end);
    });
    
    // Calculate total number of pages
    const totalPages = computed(() => {
      if (!sortedFlights.value.length) return 0;
      return Math.ceil(sortedFlights.value.length / itemsPerPage.value);
    });
    
    // Calculate page number array (maximum 5 displayed)
    const pageNumbers = computed(() => {
      if (totalPages.value <= 5) {
        return Array.from({ length: totalPages.value }, (_, i) => i);
      }
      
      // Current page is within the first 3 pages
      if (currentPage.value < 3) {
        return [0, 1, 2, 3, 4];
      }
      
      // Current page is within the last 3 pages
      if (currentPage.value > totalPages.value - 4) {
        return Array.from({ length: 5 }, (_, i) => totalPages.value - 5 + i);
      }
      
      // Current page is in the middle
      return [
        currentPage.value - 2,
        currentPage.value - 1,
        currentPage.value,
        currentPage.value + 1,
        currentPage.value + 2
      ];
    });
    
    // Login State
    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('access_token');
    });
    
    // Calculate Today's Date
    const today = computed(() => {
      const date = new Date();
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    });
    
    // Airport Search Function Timers
    const originSearchTimer = ref(null);
    const destinationSearchTimer = ref(null);
    
    // Airport Search Function (with debounce)
    const searchOriginAirports = () => {
      // Clear previous timer
      if (originSearchTimer.value) {
        clearTimeout(originSearchTimer.value);
      }
      
      // Reset dropdown if query is too short
      if (originQuery.value.length < 2) {
        originAirports.value = [];
        showOriginDropdown.value = false;
        return;
      }
      
      // Set new timer with debounce delay (300ms)
      originSearchTimer.value = setTimeout(async () => {
        try {
          const response = await searchAirports(originQuery.value);
          if (response && response.data && response.data.length) {
            originAirports.value = response.data;
            showOriginDropdown.value = true;
          }
        } catch (error) {
          console.error('Airport Search Error:', error);
        }
      }, 300); // 300ms debounce delay
    };
    
    const searchDestinationAirports = () => {
      // Clear previous timer
      if (destinationSearchTimer.value) {
        clearTimeout(destinationSearchTimer.value);
      }
      
      // Reset dropdown if query is too short
      if (destinationQuery.value.length < 2) {
        destinationAirports.value = [];
        showDestinationDropdown.value = false;
        return;
      }
      
      // Set new timer with debounce delay (300ms)
      destinationSearchTimer.value = setTimeout(async () => {
        try {
          const response = await searchAirports(destinationQuery.value);
          if (response && response.data && response.data.length) {
            destinationAirports.value = response.data;
            showDestinationDropdown.value = true;
          }
        } catch (error) {
          console.error('Airport Search Error:', error);
        }
      }, 300); // 300ms debounce delay
    };
    
    // Airport Selection Function
    const selectOrigin = (airport) => {
      originQuery.value = airport.presentation.suggestionTitle;
      selectedOrigin.value = airport;
      showOriginDropdown.value = false;
    };
    
    const selectDestination = (airport) => {
      destinationQuery.value = airport.presentation.suggestionTitle;
      selectedDestination.value = airport;
      showDestinationDropdown.value = false;
    };
    
    // Flight Search Function
    const searchFlights = async () => {
      if (!selectedOrigin.value || !selectedDestination.value || !departDate.value) {
        alert('Please enter departure, destination, and departure date.');
        return;
      }
      
      if (tripType.value === 'round' && !returnDate.value) {
        alert('Please enter return date.');
        return;
      }
      
      isLoading.value = true;
      
      try {
        const params = {
          trip_type: tripType.value,
          fromEntityId: selectedOrigin.value.navigation.relevantFlightParams.skyId,
          toEntityId: selectedDestination.value.navigation.relevantFlightParams.skyId,
          departDate: departDate.value,
          cabinClass: cabinClass.value,
          adults: adults.value,
          children: children.value,
          infants: infants.value
        };
        
        if (tripType.value === 'round') {
          params.returnDate = returnDate.value;
        }
        
        const response = await apiSearchFlights(params);
        
        // Initial search results save
        flightResults.value = response;
        
        console.log('Initial API search response:', response);
        // Always save the raw API response to localStorage for debugging
        localStorage.setItem('flightApiResponse', JSON.stringify(response));
        
        // Reset page when searching
        currentPage.value = 0;
        
        // Always try to get complete results if there's a token
        if (response.data?.token) {
          console.log('Token found in response, will try to get complete results:', response.data.token);
          
          try {
            // Always call getCompleteResults directly with the token from the response
            console.log('Calling getCompleteResults directly with token:', response.data.token);
            const completeResponse = await getCompleteResults(response.data.token);
            console.log('Complete response from direct call:', completeResponse);
            
            if (completeResponse.data?.responseType === 'itineraries' && 
                completeResponse.data?.itineraries?.length > 0) {
              
              flightResults.value.data.itineraries = completeResponse.data.itineraries;
              // Update local storage
              localStorage.setItem('flightApiResponse', JSON.stringify(completeResponse));
              console.log('Updated flight results with complete data');
            } else if (completeResponse.data?.responseType === 'error') {
              // Show a warning but keep initial results
              console.error('API error from direct call:', completeResponse.data.error);
              apiLimitReached.value = true;
              console.warn('Using initial search results due to API error');
            } else if (completeResponse.data?.responseType === 'use_initial_results') {
              // SkyScanner API는 사용할 수 없지만 초기 검색 결과는 있음
              console.warn('Using initial search results as directed by backend');
              apiLimitReached.value = true;
            }
          } catch (e) {
            console.error('Error getting complete results from direct call:', e);
            // 오류가 발생해도 초기 검색 결과를 계속 표시
            apiLimitReached.value = true;
            console.warn('Using initial search results due to error');
          }
          
          // Also try to get from saved response as a fallback (only if needed)
          if (flightResults.value.data.itineraries.length <= 10) {
            try {
              const savedResponse = localStorage.getItem('flightApiResponse');
              console.log('Saved response from localStorage:', savedResponse);
              
              if (savedResponse) {
                const parsedResponse = JSON.parse(savedResponse);
                
                // 디버깅 로그 추가
                console.log('Initial response status:', parsedResponse.data?.context?.status);
                console.log('Session ID from context:', parsedResponse.data?.context?.sessionId);
                
                // Fallback for session ID if it's not in the expected location
                const sessionId = 
                  parsedResponse.data?.context?.sessionId || 
                  parsedResponse.data?.sessionId || 
                  parsedResponse.data?.token || 
                  parsedResponse.data?.data?.token ||
                  parsedResponse.data?.flightsSessionId;
                
                console.log('Final session ID used from localStorage:', sessionId);
                
                // Only try to get complete results if we have a different session ID
                if (sessionId && sessionId !== response.data.token) {
                  // Get search results with the correct session ID
                  console.log('Calling getCompleteResults with session ID from localStorage:', sessionId);
                  const completeResponse = await getCompleteResults(sessionId);
                  console.log('Complete response from localStorage sessionId:', completeResponse);
                  
                  if (completeResponse.data?.responseType === 'itineraries' && 
                      completeResponse.data?.itineraries?.length > flightResults.value.data.itineraries.length) {
                    
                    flightResults.value.data.itineraries = completeResponse.data.itineraries;
                    // Update local storage
                    localStorage.setItem('flightApiResponse', JSON.stringify(completeResponse));
                    console.log('Updated flight results with more complete data from localStorage');
                  } else if (completeResponse.data?.responseType === 'error' || 
                             completeResponse.data?.responseType === 'use_initial_results') {
                    // 이미 초기 검색 결과를 사용 중이므로 경고만 표시
                    console.warn('Using initial search results due to API error from localStorage');
                  }
                } else {
                  console.warn('No different session ID found in localStorage or same as direct token');
                }
              }
            } catch (e) {
              console.error('Error processing search results from localStorage:', e);
              // 이미 초기 검색 결과를 사용 중이므로 계속 진행
            }
          }
        } else {
          console.warn('No token found in initial search response');
          apiLimitReached.value = true;
        }
      } catch (error) {
        alert('Flight search error occurred. Please try again.');
      } finally {
        isLoading.value = false;
      }
    };
    
    // Flight Details Page Navigation
    const viewFlightDetails = (flight) => {
      router.push({
        name: 'FlightDetails',
        query: {
          token: flightResults.value.data.token,
          itineraryId: flight.id
        }
      });
    };
    
    // View destination details page
    const viewDestinationDetails = (destination) => {
      router.push({
        name: 'FlightDetails',
        query: {
          token: flightResults.value.data.token,
          itineraryId: destination.id
        }
      });
    };
    
    // Formatting functions
    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      
      const date = new Date(dateStr);
      const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return date.toLocaleDateString('en-US', options);
    };
    
    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}hours ${mins}minutes`;
    };
    
    const getOriginDestinationText = (flight) => {
      const leg = flight.legs[0];
      return `${leg.origin.city || leg.origin.displayCode} → ${leg.destination.city || leg.destination.displayCode}`;
    };
    
    const getFlightDateInfo = (flight) => {
      const departLeg = flight.legs[0];
      
      if (flight.legs.length > 1) {
        const returnLeg = flight.legs[1];
        return `${formatDate(departLeg.departure)} - ${formatDate(returnLeg.arrival)}`;
      }
      
      return `${formatDate(departLeg.departure)}`;
    };
    
    // When the page loads, load the search history
    onMounted(() => {
      // fetchSearchHistory();
    });
    
    // Add state variables in setup() function
    const apiLimitReached = ref(false);
    
    // Destination search results pagination related state
    const destinationPage = ref(0);
    const destinationsPerPage = ref(9); // Set to 9 for 3x3 grid
    const sortOption = ref('price'); // Default sorting: lowest price
    
    // Destination results sorting function
    const sortDestinations = (option) => {
      sortOption.value = option;
      destinationPage.value = 0; // Go back to the first page when sorting
    };
    
    // Sorted destination results
    const sortedDestinations = computed(() => {
      if (!flightResults.value || 
          !flightResults.value.data || 
          !flightResults.value.data.countryDestination || 
          !flightResults.value.data.countryDestination.results) {
        return [];
      }
      
      const results = [...flightResults.value.data.countryDestination.results];
      
      switch (sortOption.value) {
        case 'price':
          return results.sort((a, b) => {
            const priceA = a.content?.flightQuotes?.cheapest?.rawPrice || Number.MAX_VALUE;
            const priceB = b.content?.flightQuotes?.cheapest?.rawPrice || Number.MAX_VALUE;
            return priceA - priceB;
          });
        case 'priceDesc':
          return results.sort((a, b) => {
            const priceA = a.content?.flightQuotes?.cheapest?.rawPrice || 0;
            const priceB = b.content?.flightQuotes?.cheapest?.rawPrice || 0;
            return priceB - priceA;
          });
        case 'name':
          return results.sort((a, b) => {
            const nameA = a.content?.location?.name || '';
            const nameB = b.content?.location?.name || '';
            return nameA.localeCompare(nameB);
          });
        default:
          return results;
      }
    });
    
    // Paginated destination results
    const paginatedDestinations = computed(() => {
      const start = destinationPage.value * destinationsPerPage.value;
      const end = start + destinationsPerPage.value;
      return sortedDestinations.value.slice(start, end);
    });
    
    // Total destination pages
    const totalDestinationPages = computed(() => {
      if (!sortedDestinations.value.length) return 0;
      return Math.ceil(sortedDestinations.value.length / destinationsPerPage.value);
    });
    
    // Destination page number array (maximum 5 displayed)
    const destinationPageNumbers = computed(() => {
      if (totalDestinationPages.value <= 5) {
        return Array.from({ length: totalDestinationPages.value }, (_, i) => i);
      }
      
      if (destinationPage.value < 3) {
        return [0, 1, 2, 3, 4];
      }
      
      if (destinationPage.value > totalDestinationPages.value - 4) {
        return Array.from({ length: 5 }, (_, i) => totalDestinationPages.value - 5 + i);
      }
      
      return [
        destinationPage.value - 2,
        destinationPage.value - 1,
        destinationPage.value,
        destinationPage.value + 1,
        destinationPage.value + 2
      ];
    });
    
    return {
      tripType,
      originQuery,
      destinationQuery,
      departDate,
      returnDate,
      cabinClass,
      adults,
      children,
      infants,
      originAirports,
      destinationAirports,
      showOriginDropdown,
      showDestinationDropdown,
      flightResults,
      isLoading,
      today,
      isAuthenticated,
      searchOriginAirports,
      searchDestinationAirports,
      selectOrigin,
      selectDestination,
      searchFlights,
      viewFlightDetails,
      viewDestinationDetails,
      formatDate,
      formatDuration,
      getOriginDestinationText,
      getFlightDateInfo,
      currentPage,
      itemsPerPage,
      totalPages,
      pageNumbers,
      paginatedFlights,
      apiLimitReached,
      destinationPage,
      destinationsPerPage,
      sortOption,
      sortDestinations,
      paginatedDestinations,
      totalDestinationPages,
      destinationPageNumbers,
      flightSortOption,
      sortFlights,
      sortedFlights
    };
  }
};
</script>

<style scoped>
:root {
  --primary-color: #4f46e5;
  --primary-dark: #4338ca;
  --primary-light: #818cf8;
  --gradient-start: #4f46e5;
  --gradient-end: #6366f1;
  --button-gradient-start: #f97316; 
  --button-gradient-end: #fb923c; 
}

.flight-container {
  background-image: url('@/assets/flight.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  min-height: 100vh;
  padding: 20px;
  margin: 0;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.container {
  max-width: 1200px;
}

h1 {
  background: linear-gradient(45deg, var(--gradient-start), var(--gradient-end));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-top: 1rem;
}

.gradient-banner {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.8), rgba(99, 102, 241, 0.8), rgba(129, 140, 248, 0.75));
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.2);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.banner-container {
  position: relative;
  width: 100%;
}

.banner-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
  border-radius: inherit;
}

.gradient-banner {
  position: relative;
  z-index: 2;
}

.search-form {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  width: 100%;
}

.search-form:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

input[type="text"], input[type="date"], input[type="number"], select {
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
  font-size: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

input[type="text"]:focus, input[type="date"]:focus, input[type="number"]:focus, select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
  outline: none;
}

.search-button {
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  border-radius: 0.75rem;
  padding: 0.875rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  color: white;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
}

.search-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.5);
  background: linear-gradient(45deg, #2563eb, #3b82f6);
}

.search-button:disabled {
  background: linear-gradient(45deg, #93c5fd, #bfdbfe);
  cursor: not-allowed;
  color: rgba(255, 255, 255, 0.8);
}

.flight-card {
  border-radius: 1rem;
  border: 1px solid rgba(235, 240, 255, 0.7);
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.flight-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  border-color: rgba(200, 224, 255, 0.8);
}

.card-header {
  background-color: rgba(240, 249, 255, 0.7);
  border-bottom: 1px solid rgba(200, 224, 255, 0.5);
}

.flight-leg {
  border-top: 1px solid #f3f4f6;
  padding-top: 1rem;
}

.details-button {
  background: var(--primary-color);
  border-radius: 0.75rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.details-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
  background: var(--primary-dark);
}

.dropdown-menu {
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.dropdown-item {
  transition: all 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.dropdown-item:hover {
  background-color: rgba(79, 70, 229, 0.05);
}

.price-tag {
  color: var(--primary-color);
  font-weight: 700;
}

.carrier-badge {
  background-color: #f5f7ff;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.carrier-badge:hover {
  background-color: #eef2ff;
  border-color: #c7d2fe;
}

.flight-duration {
  font-weight: 600;
  color: #4b5563;
}

/* Material Icons animation */
.animate-spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Pagination button style */
.pagination-button {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button:not(:disabled):hover {
  background-color: #f3f4f6;
}

/* Results summary section */
.results-summary {
  background-color: rgba(240, 249, 255, 0.7);
  border: 1px solid rgba(200, 224, 255, 0.6);
}

/* Sort buttons */
.sort-button {
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.sort-button:hover {
  border-color: #c7d2fe;
}

/* Category buttons */
.category-button {
  border-color: #c7d2fe;
  color: var(--primary-color);
}

.category-button:hover {
  background-color: rgba(79, 70, 229, 0.1);
}

/* Destination cards */
.destination-card {
  background-color: rgba(255, 255, 255, 0.9) !important;
  border-color: rgba(235, 240, 255, 0.7) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.destination-card:hover {
  border-color: rgba(200, 224, 255, 0.8) !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
}

/* Login prompt */
.login-prompt {
  background-color: rgba(240, 249, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(200, 224, 255, 0.6);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  width: 100%;
}

/* Add primary color utility classes */
.text-primary {
  color: var(--primary-color);
}

.bg-primary {
  background-color: rgba(59, 130, 246, 0.9) !important;
}

.text-primary-dark {
  color: var(--primary-dark);
}

.bg-primary-dark {
  background-color: var(--primary-dark);
}

.accent-primary {
  accent-color: var(--primary-color);
}

.banner-text {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
  line-height: 1.4;
}

.results-container {
  background-color: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
  width: 100%;
}


</style> 


