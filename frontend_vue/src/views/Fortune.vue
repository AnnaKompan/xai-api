<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4">🔮 Get Your Fortune</h2>

    <form @submit.prevent="submitKeywords">
      <div class="mb-3">
        <label class="form-label">Enter 3 Keywords 請輸入三個中文字</label>
        <input
          v-model="keywordInput"
          type="text"
          class="form-control"
          placeholder="e.g., 愛情 luck success"
          required />
      </div>

      <button class="btn btn-primary w-100" :disabled="loading">
        {{ loading ? "Checking..." : "Check Fortune" }}
      </button>
    </form>

    <div class="mt-4">
      <div v-if="message" class="alert alert-info">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Fortune",
  data() {
    return {
      keywordInput: "",
      message: "",
      loading: false,
    };
  },
  methods: {
    async submitKeywords() {
      console.log("📥 Form submitted");
      this.message = "";
      this.loading = true;

      const keywords = this.keywordInput
        .split(" ")
        .map((kw) => kw.trim().replace(/[.,!?;:，。、！？]/g, " "))
        .filter((kw) => kw !== "");

      console.log("📌 Keywords:", keywords);

      if (keywords.length !== 3) {
        this.message = "❗ Please enter exactly 3 keywords.";
        this.loading = false;
        return;
      }

      try {
        console.log("📡 Sending request to backend...");
        const response = await axios.post("http://localhost:8000/fortune", {
          keywords: keywords,
        });

        // Debug log
        console.log("💬 Backend response:", response.data);

        const data = response.data;

        switch (data.status) {
          case "success":
            this.message = data.fortune;
            break;
          case "limit_exceeded":
            this.message =
              "⚠️ You have asked for all your opportunities today.";
            break;
          case "grok_error":
            this.message = "⚠️ Today's fortune cannot be checked.";
            break;
          default:
            this.message = "⚠️ Unexpected server response.";
        }
      } catch (error) {
        console.error(error);
        this.message = "❌ Failed to connect to fortune service.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
