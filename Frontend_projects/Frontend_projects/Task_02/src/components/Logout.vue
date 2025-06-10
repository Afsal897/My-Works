<template>
  <div>
    <h2>Logging out...</h2>
  </div>
</template>

<script>
export default {
  name: "Logout",
  mounted() {
    // Clear localStorage (and sessionStorage if needed)
    localStorage.clear();
    sessionStorage.clear();

    // Redirect to login route after a short delay
    setTimeout(() => {
      this.$router.push('/login'); // Adjust to your login route
    }, 1000);
  }
};
</script>
