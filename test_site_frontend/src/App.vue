<template>
  <v-app>
    <v-main>
      <router-view/>
    </v-main>
  </v-app>
</template>
<script>
    export default {
        computed: {
            isLoggedIn: function () {
                return this.$store.getters.isLoggedIn
            }
        },
        created: function () {
            this.$http.interceptors.response.use(undefined, function (err) {
                return new Promise(function (resolve, reject) {
                    console.log(resolve, reject);
                    if (err.status === 401 && err.config && !err.config.__isRetryRequest) {
                        console.log("exit");
                        // this.$store.dispatch(logout);
                    }
                    throw err;
                });
            });
        }
    }
</script>
