<template>
  <v-app>
    <Navbar />
    <v-main class="fill-height d-flex flex-column">
      <router-view />
    </v-main>
    <AppFooter />
  </v-app>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import AppFooter from './components/AppFooter.vue'
</script>

<style>
html,
body,
#app {
  /* background-color: #0E3A4F; */
  background-color: #134B66;
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>