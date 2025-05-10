<template>
  <v-app>
    <Navbar />
    <v-main>
      <router-view />
    </v-main>
    <AppFooter />
  </v-app>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import AppFooter from './components/AppFooter.vue'
</script>
