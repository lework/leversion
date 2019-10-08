// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
// import Antd from 'ant-design-vue'
// import 'ant-design-vue/dist/antd.css'
import { message } from 'ant-design-vue'
import axios from 'axios'

Vue.config.productionTip = false
// Vue.use(Antd)
Vue.prototype.$message = message
Vue.prototype.$axios = axios

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
