<template>
    <v-container fluid class="pa-8" style="background-color: #10141a;">
      <v-row>
        <v-col cols="12">
          <h2 class="text-white mb-6">
            🧾 Chat Summary for Match {{ matchId }}
          </h2>
  
          <v-list dense class="transparent-list">
            <v-list-item
              v-for="(msg, index) in messages"
              :key="index"
              class="chat-row hoverable"
              @click="selectedMessage = msg"
            >
              <!-- Avatar -->
              <v-avatar size="50" class="mr-4">
                <v-img :src="getHeroImage(msg.hero)" />
              </v-avatar>
  
              <!-- Player info -->
              <div class="info-block">
                <div class="info-text">
                  {{ msg.time_str }} · <strong>{{ msg.player_name }}</strong> ({{ msg.hero }})
                </div>
              </div>
  
              <!-- Message -->
              <div class="message-block">
                <span
                  class="message-text"
                  :style="{ color: msg.toxic ? '#ff5e5e' : '#91f291' }"
                >
                  {{ msg.message }}
                </span>
              </div>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
  
      <!-- Dialog -->
      <v-dialog v-model="selectedMessage" max-width="600">
        <v-card :color="selectedMessage?.toxic ? 'red darken-3' : 'green darken-3'" dark>
          <v-card-title class="text-h6">
            🧝 {{ selectedMessage?.player_name }} ({{ selectedMessage?.hero }})
          </v-card-title>
          <v-card-text>
            <v-img
              :src="getHeroImage(selectedMessage?.hero)"
              height="150"
              contain
              class="mb-3"
            />
            <p><strong>🕐 Time:</strong> {{ selectedMessage?.time_str }}</p>
            <p><strong>💬 Message:</strong> {{ selectedMessage?.message }}</p>
            <p><strong>🚩 Toxic:</strong> {{ selectedMessage?.toxic ? 'Yes' : 'No' }}</p>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="selectedMessage = null">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  const matchId = route.params.matchId
  const messages = ref([])
  const selectedMessage = ref(null)
  
  onMounted(() => {
    const raw = route.query.messages
    if (raw) {
      try {
        messages.value = JSON.parse(decodeURIComponent(raw))
      } catch (err) {
        console.error("Failed to parse messages from query", err)
      }
    }
  })
  
  const getHeroImage = (heroName) => {
    if (!heroName || typeof heroName !== 'string') return ''
    return `https://cdn.dota2.com/apps/dota2/images/heroes/${heroName
      .toLowerCase()
      .replace(/ /g, '_')
      .replace(/'/g, '')}_full.png`
  }
  </script>
  
  <style scoped>
  .text-white {
    color: white;
  }
  .transparent-list {
    background-color: transparent !important;
  }
  .chat-row {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    background-color: transparent !important;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  .hoverable {
    cursor: pointer;
    transition: background-color 0.15s;
  }
  .hoverable:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
  .info-block {
    flex-shrink: 0;
    min-width: 260px;
    max-width: 320px;
  }
  .info-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
  }
  .message-block {
    flex-grow: 1;
    padding-left: 20px;
  }
  .message-text {
    font-size: 1.3rem;
    font-weight: 500;
    word-break: break-word;
  }
  </style>
  