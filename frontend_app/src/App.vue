<template>
  <router-view/>
</template>

<script>
import axios from 'axios'
import {useUserDataStore} from "@/stores/UserDataStore"
import { mapWritableState, mapStores, mapState } from "pinia";
import router from './router';

export default {
  name: 'App',
  computed: {
    ...mapStores(useUserDataStore),
    ...mapState(useUserDataStore, ['userAuthenticated']),
    ...mapWritableState(useUserDataStore, ['userAuthenticated']),
  },
  mounted() {
    axios.get(axios.defaults.baseURL + "check-cookie-login", { withCredentials: true })
    .then((response) => {
            if(response.data.status === "OK"){
              this.userAuthenticated = true
            } else{
              this.userAuthenticated = false
            }
          }).catch(error => {
              console.log(error.response.data.detail)
              router.push("login")
            })
  }
}
</script>

<style>

</style>
