<template>
    <MenuHeader></MenuHeader>



    
<main class="form-signin w-100 m-auto">
  <form @submit.prevent>
    <h1 class="h3 mb-3 fw-normal text-center">Sign In</h1>

    <div class="form-floating">
      <input v-model="userLogin" type="text" class="form-control" id="floatingInput" placeholder="Login">
      <label for="floatingInput">Login</label>
    </div>
    <div class="form-floating">
      <input v-model="userPassword" type="password" class="form-control" id="floatingPassword" placeholder="Password">
      <label for="floatingPassword">Password</label>
    </div>
    <button class="btn btn-primary w-100 py-2" type="submit" @click="loginBtnFunc">Sign in</button>
  </form>
</main>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import axios from 'axios'

export default {
    name: "LoginPage",
    components: {
    MenuHeader
  },
  data() {
    return {
      userLogin: "",
      userPassword: "",
    }
  },
  mounted() {

  },
  methods: {
    loginBtnFunc: function () {
        axios
          .post(axios.defaults.baseURL + "api/token/login", {
            login: this.userLogin,
            password: this.userPassword
          })
          .then((response) => {
            console.log(response.data);
            this.$router.push("/"); // TODO: поменять на профиль человека
          })

        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.form-signin {
  max-width: 330px;
  padding: 1rem;
}

.form-signin .form-floating:focus-within {
  z-index: 2;
}

.form-signin input[type="email"] {
  margin-bottom: -1px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.form-signin input[type="password"] {
  margin-bottom: 10px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>