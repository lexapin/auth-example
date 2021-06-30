import Vue from 'vue'
import Vuex from 'vuex'
import axios from '../plugins/axios.js'

Vue.use(Vuex);


export default new Vuex.Store({
    state: {
        status: '',
        token: localStorage.getItem('token') || '',
        user: {}
    },
    mutations: {
        auth_request(state) {
            state.status = 'loading'
        },
        auth_success(state, token) {
            state.status = 'success';
            state.token = token
            // state.user = user
        },
        auth_error(state) {
            state.status = 'error'
        },
        logout(state) {
            state.status = '';
            state.token = ''
        },
    },
    actions: {
        login({commit}, auth_data) {
            return new Promise((resolve, reject) => {
                commit('auth_request');
                axios({url: '/users/auth', data: auth_data, method: 'POST'})
                    .then(resp => {
                        console.log(resolve, reject);
                        const token = resp.data;
                        // const user = resp.data.user
                        localStorage.setItem('token', token);
                        axios.defaults.headers.common['Authorization'] = token;
                        commit('auth_success', token);
                        resolve(resp)
                    })
                    .catch(err => {
                        commit('auth_error');
                        localStorage.removeItem('token');
                        reject(err)
                    })
            })
        },
        logout({commit}) {
            return new Promise((resolve, reject) => {
                console.log(resolve, reject);
                commit('logout');
                localStorage.removeItem('token');
                delete axios.defaults.headers.common['Authorization'];
                resolve()
            })
        }
    },
    getters: {
        isLoggedIn: state => !!state.token,
        authStatus: state => state.status,
    }
})
