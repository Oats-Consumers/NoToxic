<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="pa-6" elevation="10" rounded="xl">
          <v-text-field
            v-model="gameId"
            placeholder="Enter Match ID"
            hide-details
            variant="outlined"
            density="comfortable"
            class="mb-4"
          />

          <v-btn
            color="accent"
            block
            :loading="loading"
            :disabled="!/^\d+$/.test(gameId.trim())"
            @click="fetchMessages"
          >
            Scan Chat
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
  const id = gameId.value.trim()
  if (!id) return

  loading.value = true
  error.value = null

  try {
    const { data } = await axios.get(`https://api.opendota.com/api/matches/${id}`)

    if (!data.match_id) {
      throw new Error("Invalid match ID.")
    }

    const hasParsed = data?.od_data?.has_parsed

    if (!hasParsed) {
      throw new Error("This match has not been parsed yet. Please wait and try again later.")
    }

    // ✅ Valid and parsed — go to results
    router.push({ name: 'MatchResults', params: { matchId: id } })

  } catch (err) {
    error.value = err.message || 'Invalid or unavailable match ID.'
    console.error("Validation failed:", err)
  } finally {
    loading.value = false
  }
}


</script>
