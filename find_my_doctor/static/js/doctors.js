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
        delete_mode: false,
        current_doctor_id: "",
        current_doctor_name: "",
        add_review_message: "",
        add_review_rating: 0,
        current_user_email: "",
        hovering: false,
        show_reviews: false,
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
                name: e.name, 
                address: e.address,
                // reviewed: e.reviewed,
            };
        });
        return a;
    };

    app.add_review = function () {
        axios.post(add_review_url,
            {
                doctor_name: app.vue.current_doctor_name,
                doctor_type: specialist,
                review_message: app.vue.add_review_message,
                star_rating: app.vue.add_review_rating,
            }).then(function (response) {
                app.vue.reviews.push({
                    id: response.data.id,
                    doctor_name: app.vue.current_doctor_name,
                    doctor_type: specialist,
                    review_message: app.vue.add_review_message,
                    star_rating: app.vue.add_review_rating,
                    user_email: app.vue.current_user_email,
                    name: response.data.name,
                    user_id: response.data.user_id
                });
                app.enumerate(app.vue.reviews);
                app.reset_form();
                app.set_add_status(false);
                app.vue.show_reviews = true;
            });
    };

    app.set_hovering = function (hover_status) {
        app.vue.hovering = hover_status;
    };

    app.reset_form = function() {
        app.vue.add_review_message = "";
        app.vue.add_review_rating = 0;
        app.vue.current_doctor_name = "";
    };

    app.delete_review = function (review_idx) {
        let id = app.vue.reviews[review_idx].id;
        axios.get(delete_review_url, {params: {id: id}}).then(function (response) {
            for(let i = 0; i < app.vue.reviews.length; i++){
                if(app.vue.reviews[i].id == id){
                    app.vue.reviews.splice(i, 1);
                    app.enumerate(app.vue.reviews);
                    break;
                }
            }
        });
    };

    app.set_add_status = function (new_status, doctor_row_id, doctor_row_name) {
        app.vue.add_mode = new_status;
        app.vue.current_doctor_id = doctor_row_id;
        app.vue.current_doctor_name = doctor_row_name;
    };

    app.show_delete = function (row) {
        // console.log("row email " + row.user_email)
        // console.log("current email " + app.vue.current_user_email)
        if(row.user_email === app.vue.current_user_email){
            return true;
        } else {
            return false;
        };
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_review: app.add_review,
        set_add_status: app.set_add_status,
        delete_review: app.delete_review,
        show_delete: app.show_delete,
        set_hovering: app.set_hovering,
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
            app.vue.doctors = app.enumerate(app.decorate(response.data.doctor_rows));
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
