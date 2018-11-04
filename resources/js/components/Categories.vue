<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Category</h3>
                <el-row>
                    <el-col :span="12">
                        <el-input placeholder="Category Name" v-model="category"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <el-input placeholder="Slug" v-model="slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <el-input
                                type="textarea"
                                :rows="4"
                                placeholder="Description"
                                v-model="description">
                        </el-input>
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
                    prop="slug"
                    label="Slug"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="description"
                    label="Description"
                    width="">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="Operations"
                    width="120"
                    prop="id">
                <template slot-scope="scope">
                    <el-button @click="edit(scope.$index, scope.row)" type="text" size="small">Edit</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-dialog
                title="Edit"
                :visible.sync="dialogVisible"
                width="30%"
                >
            <span>
                <el-row>
                    <el-col :span="12">
                        <el-input placeholder="Category Name" v-model="editedCategory.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <el-input placeholder="Slug" v-model="editedCategory.slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <el-input
                                type="textarea"
                                :rows="2"
                                placeholder="Description"
                                v-model="editedCategory.description">
                        </el-input>
                    </el-col>
                </el-row>
            </span>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="save()">Confirm</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import Axios from 'axios'
    export default {
        name: "Categories",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                category: '',
                description: '',
                slug: '',
                editedCategory: {},
                categories: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewCategory() {
                let $this = this;
                let params = {};
                params.category = this.category;
                params.description = this.description;
                params.slug = this.slug;
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
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.categories = data.categories;
            },
            clearForm() {
                this.category = '';
                this.slug = '';
                this.description = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedCategory = row;
            },
            save() {
                let $this = this;
                let params = this.editedCategory;
                Axios.post('/dashboard/category/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedCategory = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>