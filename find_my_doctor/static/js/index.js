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

    app.add_symptom = function (symptom_name) {
        //need to push and crap, plus add this to methods list
        newSymptom =
            app.vue.symptom_list.push({ symptom_name: symptom_name });
        axios.post(update_symptom_url, { symptom_name: symptom_name });
        app.enumerate(app.vue.symptom_list);
        app.vue.query = "";
        app.vue.results = [];
    }


    //need to grab user's symptoms and put into symptom_list during init

    app.remove_symptom = function (symptom_name) {
        for (let i = 0; i < app.vue.symptom_list.length; i++) {
            if (app.vue.symptom_list[i].symptom_name === symptom_name) {
                app.vue.symptom_list.splice(i, 1);
                app.enumerate(app.vue.symptom_list);
                break;
            }
        }
        axios.post(delete_symptom_url, { symptom: symptom_name })
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

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        add_symptom: app.add_symptom,
        remove_symptom: app.remove_symptom,
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

        axios.get(load_symptoms_url).then(function (response) {
            app.vue.symptom_list = app.enumerate(response.data.symptom_list);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
