<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="pa-4" elevation="10" rounded="xl">
          <v-card-title class="text-h5 text-center">
            🎮 Dota 2 Match Viewer
          </v-card-title>

          <v-text-field
            v-model="gameId"
            label="Enter Match ID"
            outlined
            dense
            class="mb-4"
          />

          <v-btn
            color="primary"
            block
            :loading="loading"
            @click="fetchMessages"
          >
            Get Chat Messages
          </v-btn>

          <v-alert
            type="error"
            v-if="error"
            class="mt-4"
            dense
            text
          >
            {{ error }}
          </v-alert>

          <v-list two-line class="mt-4" v-if="messages.length">
            <v-list-item
              v-for="(msg, index) in messages"
              :key="index"
              class="mb-2"
            >
              <v-list-item-content>
                <v-list-item-title>{{ msg.author }}</v-list-item-title>
                <v-list-item-subtitle>{{ msg.text }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>

          <v-alert
            v-else-if="!loading"
            type="info"
            class="mt-4"
            text
          >
            Enter a match ID and click the button to see messages.
          </v-alert>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router' // ✅ FIXED: Import useRouter
import axios from 'axios'

const router = useRouter() // ✅ FIXED: Create router instance
const gameId = ref('')
const messages = ref([])
const loading = ref(false)
const error = ref(null)

const fetchMessages = async () => {
  if (!gameId.value.trim()) return

  loading.value = true
  error.value = null
  messages.value = []

  try {
    const res = await axios.get(`http://127.0.0.1:5000/get-toxic-messages?match_id=${gameId.value}`)
    
    if (res.data.error) {
      throw new Error(res.data.error)
    }

    router.push({
      name: 'MatchResults',
      params: { matchId: gameId.value },
      query: { messages: encodeURIComponent(JSON.stringify(res.data.messages)) }
    })

  } catch (err) {
    error.value = 'Failed to fetch messages. Check the match ID or server.'
    console.error("Fetch failed:", err)
  } finally {
    loading.value = false
  }
}
</script>
