<template>
  <v-data-table
    :headers="headers"
    :items="users"
    hide-default-footer
    sort-by="calories"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar
        flat
      >
        <v-toolbar-title>Пользователи</v-toolbar-title>
        <v-divider
          class="mx-4"
          inset
          vertical
        ></v-divider>
        <v-dialog
          v-model="dialog"
          max-width="500px"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              color="primary"
              dark
              class="mb-2"
              v-bind="attrs"
              v-on="on"
            >
              Добавить нового пользователя
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="text-h5">{{ formTitle }}</span>
            </v-card-title>

            <v-card-text>
              <v-container>
                <v-row>
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                    <v-text-field
                      v-model="editedItem.email"
                      label="Почта/Логин"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                    <v-checkbox
                      v-model="editedItem.view"
                      label="Просмотр"
                    ></v-checkbox>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                    <v-checkbox
                      v-model="editedItem.edit"
                      label="Редактирование"
                    ></v-checkbox>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                    <v-checkbox
                      v-model="editedItem.create"
                      label="Создание"
                    ></v-checkbox>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="blue darken-1"
                text
                @click="close"
              >
                Cancel
              </v-btn>
              <v-btn
                color="blue darken-1"
                text
                @click="save"
              >
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title class="text-h5">Точно удалить?</v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="closeDelete">Отмена</v-btn>
              <v-btn color="blue darken-1" text @click="deleteItemConfirm">Удалить</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-spacer></v-spacer>
        <v-btn @click="logout">
          <span class="mr-2">Выход</span>
          <v-icon>mdi-logout</v-icon>
        </v-btn>
      </v-toolbar>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-icon
        small
        class="mr-2"
        @click="editItem(item)"
      >
        mdi-pencil
      </v-icon>
      <v-icon
        small
        @click="deleteItem(item)"
      >
        mdi-delete
      </v-icon>
    </template>
    <template v-slot:item.view="{ item }">
      <v-simple-checkbox
        v-model="item.view"
        disabled
      ></v-simple-checkbox>
    </template>
    <template v-slot:item.edit="{ item }">
      <v-simple-checkbox
        v-model="item.edit"
        disabled
      ></v-simple-checkbox>
    </template>
    <template v-slot:item.create="{ item }">
      <v-simple-checkbox
        v-model="item.create"
        disabled
      ></v-simple-checkbox>
    </template>
    <template v-slot:no-data>
      <v-btn
        color="primary"
        @click="initialize"
      >
        Reset
      </v-btn>
    </template>
  </v-data-table>
</template>
<script>
  export default {
    data: () => ({
      dialog: false,
      dialogDelete: false,
      headers: [
        {
          text: 'Почта/Логин',
          align: 'start',
          sortable: false,
          value: 'email',
        },
        { text: 'Просмотр', value: 'view' },
        { text: 'Редактирование', value: 'edit' },
        { text: 'Создание', value: 'create' },
        { text: 'Действия', value: 'actions', sortable: false },
      ],
      users: [],
      editedIndex: -1,
      editedItem: {
        id: null,
        email: '',
        view: false,
        edit: false,
        create: false,
      },
      defaultItem: {
        id: null,
        email: '',
        view: true,
        edit: false,
        create: false,
      },
    }),

    computed: {
      formTitle () {
        return this.editedIndex === -1 ? 'Новый пользователь' : 'Редактирование'
      },
    },

    watch: {
      dialog (val) {
        val || this.close()
      },
      dialogDelete (val) {
        val || this.closeDelete()
      },
    },

    created () {
      this.initialize()
    },

    methods: {
      initialize () {
        new Promise(() => {
            this.$axios({url: '/users/', method: 'GET'})
            .then((response) => {
                for (const user_data of response.data) {
                    console.log(user_data);
                    this.users.push({
                        id: user_data.id,
                        email: user_data.email,
                        view: Boolean(0x01 & user_data.permissions),
                        edit: Boolean(0x02 & user_data.permissions),
                        create: Boolean(0x04 & user_data.permissions),
                    })
                }
            })
            .catch(err => {
                console.log(err);
            });
        });
      },

      editItem (item) {
        this.editedIndex = this.users.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.dialog = true
      },

      deleteItem (item) {
        this.editedIndex = this.users.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.dialogDelete = true
      },

      deleteItemConfirm () {
          new Promise(() => {
            const edited_index = this.editedIndex;
            this.$axios.delete(`/users/${this.editedItem.id}`)
                .then((response) => {
                    console.log(response);
                    this.users.splice(edited_index, 1);
                })
                .catch(err => {
                    alert("Ошибка удаления", err);
                });
            });
          this.closeDelete()
      },

      close () {
        this.dialog = false
        this.$nextTick(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        })
      },

      closeDelete () {
        this.dialogDelete = false
        this.$nextTick(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        })
      },

      save () {
        if (this.editedIndex > -1) {
          new Promise(() => {
            const can_view = (this.editedItem.view) ? 0x01 : 0x00;
            const can_edit = (this.editedItem.edit) ? 0x02 : 0x00;
            const can_create = (this.editedItem.create) ? 0x04 : 0x00;
            const new_permissions = can_view | can_edit | can_create;
            const edited_index = this.editedIndex;
            let data = {
                id: this.editedItem.id,
                email: this.editedItem.email,
                permissions: new_permissions
            };
            console.log(data);
            this.$axios.put('/users/', data)
            .then((response) => {
                console.log(response.data);
                Object.assign(this.users[edited_index], {
                    id: response.data.id,
                    email: response.data.email,
                    view: Boolean(0x01 & response.data.permissions),
                    edit: Boolean(0x02 & response.data.permissions),
                    create: Boolean(0x04 & response.data.permissions),
                })
            })
            .catch(err => {
                alert("Ошибка сохранения данных", err);
            })
          });
        } else {
            new Promise(() => {
                const can_view = (this.editedItem.view) ? 0x01 : 0x00;
                const can_edit = (this.editedItem.edit) ? 0x02 : 0x00;
                const can_create = (this.editedItem.created) ? 0x04 : 0x00;
                const new_permissions = can_view | can_edit | can_create;
                let data = {
                    email: this.editedItem.email,
                    permissions: new_permissions
                };
                console.log(data);
                this.$axios.post('/users/', data)
                    .then((response) => {
                        console.log(response.data);
                        this.users.push({
                            id: response.data.id,
                            email: response.data.email,
                            view: Boolean(0x01 & response.data.permissions),
                            edit: Boolean(0x02 & response.data.permissions),
                            create: Boolean(0x04 & response.data.permissions),
                        })
                    })
                    .catch(err => {
                        alert("Ошибка создания нового пользователя", err);
                    });
            });
        }
        this.close()
      },

      logout: function () {
        this.$store.dispatch('logout')
        .then(() => {
            this.$router.push('/login')
        })
      }
    },
  }
</script>
