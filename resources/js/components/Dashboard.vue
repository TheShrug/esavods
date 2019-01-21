<template>
    <div class="dashboard-container row">
        <div class="col-md-2">
            <div class="list-group">
                <a href="#" v-for="item in sections" class="list-group-item" @click="changeSection(item)">{{ item }}</a>
            </div>
        </div>
        <div class="col-md-10">
            <div class="dashboard bg-secondary">
                <runs v-if="selectedSection === 'Runs'"></runs>
                <categories v-if="selectedSection === 'Categories'"></categories>
                <events v-if="selectedSection === 'Events'"></events>
                <runners v-if="selectedSection === 'Runners'"></runners>
                <platforms v-if="selectedSection === 'Platforms'"></platforms>
                <games v-if="selectedSection === 'Games'"></games>
                <genres v-if="selectedSection === 'Genres'"></genres>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        name: "dashboard",
        data: function() {
            return {
                sections:  ['Runs', 'Categories', 'Events', 'Runners', 'Platforms', 'Games', 'Genres'],
                selectedSection: 'Runs'
            }
        },
        methods: {
            changeSection(section) {
                this.selectedSection = section;
            }
        }
    }
</script>
<style scoped>
    .dashboard-container {
        width: 100%;
    }
    .dashboard {
        border-radius:.25rem;
    }
</style>