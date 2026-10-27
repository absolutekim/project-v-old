import { createRouter, createWebHistory } from 'vue-router';
import WelcomeView from '@/views/WelcomeView.vue';
import RegisterView from '@/views/RegisterView.vue';
import LoginView from '@/views/LoginView.vue';
import PostDetailView from '@/views/PostDetailView.vue';
import NewPostView from '@/views/NewPostView.vue';
import EditPostView from '@/views/EditPostView.vue';
import CommunityView from '@/views/CommunityView.vue';
import DestinationList from '@/views/DestinationList.vue';
import DestinationDetailView from '@/views/DestinationDetailView.vue';
import DestinationRecommend from '@/views/DestinationRecommend.vue';
import MyPage from '@/views/MyPage.vue';
import ProfileView from '../views/ProfileView.vue'
import MostLoved from '../views/MostLoved.vue'
import CreatePlanner from '@/views/CreatePlanner.vue';
import NearbyLocations from '@/components/NearbyLocations.vue';
import FlightView from '@/views/FlightView.vue';


/**
 * Routes configuration for the application
 * Each route maps a URL path to a Vue component
 * Some routes have meta fields to specify authentication requirements
 */
const routes = [
  { path: '/', component: WelcomeView },
  { path: '/register', component: RegisterView },
  { path: '/login', component: LoginView },
  { path: '/community', component: CommunityView, meta: { requiresAuth: true } },
  { path: '/community/:id', component: PostDetailView, props: true, meta: { requiresAuth: true } },
  { path: '/community/new', component: NewPostView, meta: { requiresAuth: true } },
  { path: '/community/:id/edit', component: EditPostView, props: true, meta: { requiresAuth: true } },
  { path: '/destinations', component: DestinationList },
  { path: '/destinations/:id', component: DestinationDetailView, props: true },
  { path: '/recommendations', component: DestinationRecommend, meta: { requiresAuth: true } },
  { path: '/mypage', component: MyPage, meta: { requiresAuth: true } },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/most-loved',
    name: 'MostLoved',
    component: MostLoved
  },
  {
    path: '/planner',
    name: 'Planner',
    component: CreatePlanner,
    meta: { requiresAuth: true }
  },
  {
    path: '/nearby',
    name: 'NearbyLocations',
    component: NearbyLocations
  },
  {
    path: '/flights',
    name: 'Flights',
    component: FlightView
  },
  {
    path: '/flights/details',
    name: 'FlightDetails',
    component: () => import('@/views/FlightDetailView.vue'),
    props: (route) => ({ 
      token: route.query.token,
      itineraryId: route.query.itineraryId
    })
  },
];

/**
 * Create Vue Router instance with HTML5 history mode
 * This enables cleaner URLs without the hash (#) symbol
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * Global navigation guard
 * Prevents unauthorized access to protected routes
 * Redirects to login page if authentication is required but user is not logged in
 */
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    alert("Login required to access this page.");
    next('/login'); // Redirect to login page
  } else {
    next();
  }
});

export default router;
