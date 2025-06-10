<template>
  <div class="container mt-5">
    <router-link 
      to="/logout" 
      class="btn btn-danger position-absolute top-0 end-0 m-3"
    >
      Logout
    </router-link>
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow">
          <div class="card-body">
            <h2 class="card-title text-center mb-4">Calculator</h2>
            
            <div class="row g-3 mb-4">
              <div class="col">
                <input
                  v-model="num1"
                  type="text"
                  class="form-control"
                  placeholder="First number"
                >
              </div>
              <div class="col">
                <input
                  v-model="num2"
                  type="text"
                  class="form-control"
                  placeholder="Second number"
                >
              </div>
            </div>

            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="result !== null" class="alert alert-success">
              Result: <strong>{{ result }}</strong>
            </div>

            <div class="d-grid gap-2 d-flex justify-content-center">
              <button
                v-for="op in operations"
                :key="op.name"
                @click="performOperation(op.name)"
                class="btn btn-outline-primary"
                :disabled="!isValid"
              >
                <i :class="op.icon" class="me-1"></i> {{ op.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      num1: '',
      num2: '',
      result: null,
      error: '',
      operations: [
        { name: 'add', label: 'Add', icon: 'bi bi-plus-lg' },
        { name: 'subtract', label: 'Subtract', icon: 'bi bi-dash-lg' },
        { name: 'multiply', label: 'Multiply', icon: 'bi bi-x-lg' },
        { name: 'division', label: 'Divide', icon: 'bi bi-slash-lg' }
      ]
    }
  },
  computed: {
    isValid() {
      return this.isNumber(this.num1) && this.isNumber(this.num2)
    }
  },
  mounted() {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      this.$router.push('/login')
      return
    }

    // Optional: Verify token validity via API
    axios.get('http://localhost:5000/verify-token', {
      headers: { Authorization: `Bearer ${token}` }
    }).catch(() => {
      localStorage.removeItem('accessToken')
      this.$router.push('/login')
      return;
    })
  },
  methods: {
  isNumber(value) {
    return /^-?\d+(\.\d+)?$/.test(value)
  },
  async performOperation(operation) {
    this.error = ''
    this.result = null

    if (!this.isValid) {
      this.error = 'Both inputs must be valid numbers.'
      return
    }

    try {
      const response = await axios.get(`http://localhost:5000/${operation}`, {
        params: {
          a: parseFloat(this.num1),
          b: parseFloat(this.num2)
        },
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`
        }
      })
      this.result = response.data.output
    } catch (error) {
      this.handleError(error, operation)
    }
  },
  handleError(error, operation) {
    if (error.response) {
      const status = error.response.status

      if (status === 401 || status === 422) {
        this.error = 'Session expired or invalid input. Redirecting to login...'
        localStorage.removeItem('accessToken')
        setTimeout(() => this.$router.push('/login'), 1500)
      } else if (status === 400) {
        this.error = 'Invalid input. Please check your numbers.'
      } else if (status === 500 && operation === 'division') {
        this.error = 'Cannot divide by zero.'
      } else {
        this.error = error.response.data.error || 'An unknown error occurred.'
      }
    } else {
      this.error = 'Network error. Please check your internet connection.'
    }
  }
}

}
</script>

<style scoped>
.card {
  border-radius: 15px;
}

.btn-outline-primary {
  width: 140px;
}

.alert {
  margin-top: 1rem;
}

.me-1 {
  margin-right: 0.5rem;
}
</style>


<style scoped>
.card {
  border-radius: 15px;
}

.btn-outline-primary {
  width: 120px;
}

.alert {
  margin-top: 1rem;
  margin-bottom: 0;
}
</style>

<!-- <style scoped>
/* Remove number input arrows */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type=number] {
  -moz-appearance: textfield;
}
</style> -->