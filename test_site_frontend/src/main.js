import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import store from './store/index.js'
import router from './router.js'
import axios from './plugins/axios.js'

Vue.config.productionTip = false;
Vue.prototype.$http = axios;
Vue.prototype.$axios = axios;

const token = localStorage.getItem('token');
if (token) {
  Vue.prototype.$http.defaults.headers.common['Authorization'] = token
}

axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  console.log(error.response.data);
  if (error.response.status === 401) {
    store.dispatch('logout');
    router.push('/login')
  }
  return Promise.reject(error)
});

new Vue({
  router,
  vuetify,
  store,
  render: h => h(App)
}).$mount('#app');
