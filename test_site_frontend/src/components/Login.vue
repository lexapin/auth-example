<template>
    <v-container style="margin-top: 4rem;">
        <v-row
            v-if="auth_error"
            class="justify-center"
        >
            <v-alert
              outlined
              min-width="80%"
              type="error"
              text
            >
                <div>{{auth_error.detail.msg}}</div>
                <v-divider
                    class="my-2 error"
                    style="opacity: 0.22"
                ></v-divider>
            </v-alert>
        </v-row>
        <v-row class="text-center">
            <v-col class="mb-4">
                <h4 class="display-2 font-weight-medium">
                    Вход
                </h4>
            </v-col>
        </v-row>
        <v-row class="justify-center">
            <v-col class="mb-6 display-2" cols="8">
                <v-text-field
                    v-model="email"
                    :error-messages="emailErrors"
                    label="Адрес электронной почты"
                    required
                    @input="$v.email.$touch()"
                    @blur="$v.email.$touch()"
                ></v-text-field>
            </v-col>
        </v-row>
        <v-row class="justify-center" justify="space-around">
            <v-btn
                color="success"
                elevation="8"
                medium
                @click="login"
            >Войти</v-btn>
        </v-row>
    </v-container>
</template>
<script>
    import { validationMixin } from 'vuelidate'
    import { required, email } from 'vuelidate/lib/validators'
    export default {
        mixins: [validationMixin],

        validations: {
            email: { required, email },
        },

        data(){
            return {
                email : "",
                auth_error: null
            }
        },

        computed: {
            emailErrors () {
                const errors = [];
                if (!this.$v.email.$dirty) return errors;
                !this.$v.email.email && errors.push('Неправильный формат адреса почты');
                !this.$v.email.required && errors.push('Обязательное значение');
                return errors
            },
        },

        methods: {
            login () {
                this.$v.$touch();
                if (this.$v.$anyError) return;
                let email = this.email;

                this.$store.dispatch('login', { email, })
                .then(() => this.$router.push('/'))
                .catch(err => {
                    if (err.response && err.response.status === 404)
                        this.auth_error = {
                            detail: {msg: "Пользователь не найден"}
                        };
                    else
                        this.auth_error = {
                            detail: {msg: "Произошла ошибка авторизации"}
                        }
                });
            }
        }
    }
</script>