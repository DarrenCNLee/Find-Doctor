// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        results: [],
        symptom_list: [],
        doctors: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    app.add_symptom = function() {
        app.vue.symptom_list.push(app.vue.query);
        app.vue.query = "";
        app.vue.results = [];
    }

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, { params: { q: app.vue.query } })
                .then(function (result) {
                    app.vue.results = result.data.results;
                });
        } else {
            app.vue.results = [];
        }
    }

    app.set_stars = (doctor_idx, num_stars) => {
        let doctor = app.vue.doctors[doctor_idx];
        doctor.rating = num_stars;
        axios.post(set_rating_url, { doctor_id: doctor.id, rating: num_stars });
    };

    app.stars_out = (doctor_idx) => {
        let doctor = app.vue.doctors[doctor_idx];
        doctor.num_starts_display = doctor.rating;
    };

    app.stars_over = (doctor_idx, num_stars) => {
        let doctor = app.vue.doctors[doctor_idx];
        doctor.num_stars_display = num_stars;
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        add_symptom: app.add_symptom,
        set_stars: app.set_stars,
        stars_out: app.stars_out,
        stars_over: app.stars_over,
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

        axios.get(get_doctors_url)
            .then((result) => {
                let doctors = result.data.doctors;
                app.enumerate(doctors);
                app.complete(doctors);
                app.vue.doctors = doctors;
            })
            .then(() => {
                for (let doctor of app.vue.doctors) {
                    axios.get(get_rating_url, { params: { "doctor_id": doctor.id } })
                        .then((result) => {
                            doctor.rating = result.data.rating;
                            doctor.num_stars_display = result.data.rating
                        });
                }
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);