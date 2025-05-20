<template>
  <nav>
    <ul>
      <li><router-link to="/">Browse</router-link></li>
      <li><router-link to="/home">Home</router-link></li>
      <li><router-link to="/fortune">Fortune</router-link></li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: "NavBar",
};
</script>

<style>
nav {
  background-color: #f8f9fa;
  padding: 1rem;
}

nav ul {
  list-style-type: none;
  padding: 0;
  display: flex;
  gap: 1rem;
}

nav ul li {
  display: inline;
}

nav ul li a {
  text-decoration: none;
  color: #007bff;
}

nav ul li a:hover {
  text-decoration: underline;
}
</style>
