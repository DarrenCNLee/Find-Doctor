// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        add_mode: false,
        current_doctor_id: 0,
        add_review_message: "",
        add_review_rating: 0,
        current_user_email: "",
        doctors: [],
        reviews: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    app.decorate = (a) => {
        a.map((e) => {
            e._server_vals = {
                text: e.text, 
                author: e.author, 
                cur: e.cur, 
                reaction: e.reaction,
                reacters: e.reacters,
            };
        });
        return a;
    };

    app.add_review = function () {
        axios.post(add_review_url,
            {
                doctor_id: app.vue.current_doctor_id,
                review_message: app.vue.add_review_message,
                star_rating: app.vue.add_review_rating,
            }).then(function (response) {
                app.vue.reviews.push({
                    id: response.data.id,
                    doctor_id: app.vue.current_doctor_id,
                    review_message: app.vue.add_review_message,
                    star_rating: app.vue.add_review_rating,
                    name: response.data.name,
                    user_id: response.data.user_id
                });
                app.enumerate(app.vue.reviews);
                app.reset_form();
                app.set_add_status(false);
            });
    };

    app.reset_form = function() {
        app.vue.add_review_message = "";
        app.vue.add_review_rating = 0;
    };

    app.set_add_status = function (new_status, doctor_row_id) {
        app.vue.add_mode = new_status;
        app.vue.current_doctor_id = doctor_row_id
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_review: app.add_review,
        set_add_status: app.set_add_status,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_reviews_url).then(function (response) {
            app.vue.doctors = app.enumerate(response.data.doctor_rows);
            app.vue.reviews = app.enumerate(response.data.review_rows);
            app.vue.users = app.enumerate(response.data.user_rows);
            app.vue.current_user_email = response.data.current_user_email;
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
