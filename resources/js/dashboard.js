import Vue from 'vue';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import locale from 'element-ui/lib/locale/lang/en'

Vue.use(ElementUI, { locale })

/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

Vue.component('dashboard', require('./components/Dashboard'));
Vue.component('runs', require('./components/Runs'));
Vue.component('categories', require('./components/Categories'));
Vue.component('events', require('./components/Events'));
Vue.component('runners', require('./components/Runners'));
Vue.component('platforms', require('./components/Platforms'));
Vue.component('games', require('./components/Games'));
Vue.component('genres', require('./components/Genres'));

let dashboardExists = document.getElementById('dashboard');

if(dashboardExists) {
    const app = new Vue({
        el: '#dashboard'
    });
}
