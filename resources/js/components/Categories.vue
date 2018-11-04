<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Category</h3>
                <el-row>
                    <el-col :span="12">
                        <el-input placeholder="Category Name" v-model="category"></el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <button @click="addNewCategory" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="categories"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Category"
                    width="">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="Operations"
                    width="120">
                <template slot-scope="scope">
                    <el-button type="text" size="small">Detail</el-button>
                    <el-button type="text" size="small">Edit</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
    import Axios from 'axios'
    export default {
        name: "Runs",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                category: '',
                categories: []
            }
        },
        methods: {
            addNewCategory() {
                let $this = this;
                let params = {};
                params.category = this.category;
                Axios.post('/dashboard/category', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/category', {})
                    .then(function(response){
                        console.log(response);
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.categories = data.categories;
            },
            clearForm() {
                this.category = '';

            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>