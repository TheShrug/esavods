<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Game</h3>
                <el-row>
                    <el-col :span="12">
                        <span>Game Name</span>
                        <el-input placeholder="Game Name" v-model="game"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
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
                        <button @click="addNewGame" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="games"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Game"
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
                    <el-button @click="deleteGame(scope.$index, scope.row)" type="text" size="small"><i class="fa fa-trash"></i></el-button>
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
                        <span>Game Name</span>
                        <el-input placeholder="Game Name" v-model="editedGame.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="editedGame.slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
                        <el-input
                                type="textarea"
                                :rows="2"
                                placeholder="Description"
                                v-model="editedGame.description">
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
        name: "Games",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                game: '',
                description: '',
                slug: '',
                editedGame: {},
                games: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewGame() {
                let $this = this;
                let params = {};
                params.game = this.game;
                params.description = this.description;
                params.slug = this.slug;
                Axios.post('/dashboard/game', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/game', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.games = data.games;
            },
            clearForm() {
                this.game = '';
                this.slug = '';
                this.description = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedGame = row;
            },
            deleteGame(index, row) {
                let $this = this;
                let id = _.get(row, 'id', '');
                if(confirm('are you sure?')) {
                    Axios.delete('/dashboard/game/' + id)
                        .then(function(response){
                            $this.setFromJson(response.data);
                        });
                }
            },
            save() {
                let $this = this;
                let params = this.editedGame;
                Axios.post('/dashboard/game/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedGame = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>