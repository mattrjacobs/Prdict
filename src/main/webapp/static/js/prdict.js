// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
    window.Game = Backbone.Model.extend({
        validate: function(attrs) {
            if (attrs.key.length < 1) return "Game must have a key";
            if (attrs.home_team_name.length < 1) return "Game must have a home team";
            if (attrs.away_team_name.length < 1) return "Game must have an away team";
        }
    });

    window.CollectionGames = Backbone.Collection.extend({
        model: Game,
    });

    /**
     * Fetch called by a UI action - just use Backbone's
     * It will fire a change event if server state different from internal
     */
    window.PaginatedGamesWrapper = Backbone.Model.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON PaginatedGamesWrapper");
            this.collection = new CollectionGames([]);
        },
        parse: function(response) {
            if (response["events"]) {
                this.startIndex = response["events"]["start-index"];
                this.maxResults = response["events"]["max-results"];
                this.totalResults = response["events"]["total-results"];
                var rawGames = response["events"]["items"];
                var modelGames = rawGames.map(function(gameJson) {
                    modelGame = new Game({
                        home_team_name : gameJson["home_team"]["title"],
                        home_team_location : gameJson["home_team"]["location"],
                        home_team_score : gameJson["home_team"]["score"],
                        away_team_name : gameJson["away_team"]["title"],
                        away_team_location : gameJson["away_team"]["location"],
                        away_team_score : gameJson["away_team"]["score"],
                        key : gameJson["key"],
                        cancelled : gameJson["cancelled"],
                        start_date : gameJson["start_date"]
                    });
                    return modelGame;
                });
                this.collection.reset(modelGames);
            }
        }
    });

    // Create our global wrappers  of **Games**.
    window.WrapperGamesRecent = PaginatedGamesWrapper.extend({
        url: "/api/events/recent"
    });
    window.WrapperGamesInProgress = PaginatedGamesWrapper.extend({
        url: "/api/events/inprogress"
    });
    window.WrapperGamesUpcoming = PaginatedGamesWrapper.extend({
        url: "/api/events/future"
    });

    window.UpdatingWrapperView = Backbone.View.extend({
        initialize: function(options) {
            console.info("INIT CALLED ON UpdatingWrapperView")

            _(this).bindAll('change');
            this.model.bind('change', this.change);

            this._collectionView = new UpdatingCollectionView({
                collection:           this.model.collection,
                childViewConstructor: options.childViewConstructor,
                buttonText:           options.buttonText,
                buttonClass:          options.buttonClass,
                showScore:            options.showScore,
                el:                   options.el
            });
        },

        change: function(wrappedCollection) {
            console.info("CHANGE called on Wrapper");
            var unwrappedCollection  = wrappedCollection.get("events")["items"];
            this.model.collection.reset(wrappedCollection);
        }
    });

    window.UpdatingCollectionView = Backbone.View.extend({
        initialize : function(options) {
            console.info("INIT CALLED ON UpdatingCollectionView");
            _(this).bindAll('add', 'reset', 'remove');
 
            if (!options.childViewConstructor) throw "no child view constructor provided";
 
            this._childViewConstructor = options.childViewConstructor;
            this._buttonText =           options.buttonText;
            this._buttonClass =          options.buttonClass;
            this._showScore =            options.showScore;
 
            this._childViews = [];
 
            _(this.collection).each(this.add);
 
            this.collection.bind('add', this.add);
            this.collection.bind('remove', this.remove);
            this.collection.bind('reset', this.reset);
        },
 
        add : function(item) {
            var childView = new this._childViewConstructor({
                model :      item,
                buttonText:  this._buttonText,
                buttonClass: this._buttonClass,
                showScore:   this._showScore
            });
            
            this._childViews.push(childView);
 
            if (this._rendered) {
                $(this.el).append(childView.render().el);
            }
        },
 
        remove : function(model) {
            var viewToRemove = _(this._childViews).select(function(cv) { 
                return cv.model === model; })[0];
            this._childViews = _(this._childViews).without(viewToRemove);
            
            if (this._rendered) $(viewToRemove.el).remove();
        },

        reset : function(newCollection) {
            this._childViews = [];
            var that = this;
            newCollection.each(function(item) {
                that.add(item);
            });
            this.render()
        },
 
        render : function() {
            var that = this;
            this._rendered = true;
 
            $(this.el).empty();
 
            _(this._childViews).each(function(childView) {
                $(that.el).append(childView.render().el);
            });
 
            return this;
        }
    });

    window.GameView = Backbone.View.extend({
        tagName: "div",
        className: "game",
        template: _.template($('#game-template').html()),

        render : function() {
            $(this.el).html(this.template({
                home_title:   this.model.get("home_team_name"),
                away_title:   this.model.get("away_team_name"),
                home_score:   this.model.get("home_team_score"),
                away_score:   this.model.get("away_team_score"),
                event_key:    this.model.get("key"),
                button_text:  this._buttonText,
                button_class: this._buttonClass,
                show_score:   this._showScore
            }));
            return this;
        }
    });

    window.UpdatingGameView = GameView.extend({
        initialize: function(options) {
            this.render = _.bind(this.render, this);
            this.model.bind('change', this.render);
            this.model.bind('add', this.render);
 
            this._buttonText =  options.buttonText;
            this._buttonClass = options.buttonClass;
            this._showScore =   options.showScore;
        }
    });

    // The Application
    // ---------------
    
    // Our overall **AppView** is the top-level piece of UI.
    window.AppView = Backbone.View.extend({
        
        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: $("#allgames"),
        
        // Our template for the line of statistics at the bottom of the app.
        //statsTemplate: _.template($('#stats-template').html()),
        
        events: {
            "change #league_filter": "selectLeague",
            "click #refresh": "refreshAll"
        },
        
        initialize: function() {
            console.info("INIT The Appview!!!!");

            this._gamesInProgressView = new UpdatingWrapperView({
                model : this.model.gamesInProgress,
                childViewConstructor : UpdatingGameView,
                buttonText : "Prdict!",
                buttonClass : "primary",
                showScore: true,
                el : $('#inprogress')[0]
            });

            this._gamesUpcomingView = new UpdatingWrapperView({
                model : this.model.gamesUpcoming,
                childViewConstructor : UpdatingGameView,
                buttonText : "Chat",
                buttonClass : "small info",
                showScore: false,
                el : $('#upcoming')[0]
            });

            this._gamesRecentView = new UpdatingWrapperView({
                model : this.model.gamesRecent,
                childViewConstructor : UpdatingGameView,
                buttonText : "Replay",
                buttonClass : "small info",
                showScore: true,
                el : $('#recent')[0]
            });
            
            this.fetchAll();
        },
        
        render: function() {
            console.info("RENDER AT TOPLEVEL (nothing to do)!!!!");
        },

        fetchAll: function() {
            this.model.gamesInProgress.fetch({dataType: "json"});
            this.model.gamesUpcoming.fetch({dataType: "json"});
            this.model.gamesRecent.fetch({dataType: "json"});
        },

        fetchByLeague: function(league_name) {
            console.info("FETCHING BY LEAGUE : " + league_name);
            this._current_query = {"league" : league_name};
            var ajaxParams = {
                dataType: "json",
                data: {
                    league: league_name
                }
            };
            this.model.gamesInProgress.fetch(ajaxParams);
            this.model.gamesUpcoming.fetch(ajaxParams);
            this.model.gamesRecent.fetch(ajaxParams);
        },

        refreshAll: function() {
            console.info("REFRESH ALL views");
            if (this._current_query) {
                league_name = this._current_query.league;
                if (league_name) {
                    this.fetchByLeague(league_name);
                } else {
                    this.fetchAll();
                }
            } else {
                this.fetchAll();
            }
        },

        selectLeague: function(e) {
            this.fetchByLeague(e.currentTarget.value);
        }
    });
    
    // Finally, we kick things off by creating the **App**.
    window.App = new AppView({model: {'gamesInProgress' : new WrapperGamesInProgress,
                                      'gamesUpcoming'   : new WrapperGamesUpcoming,
                                      'gamesRecent'     : new WrapperGamesRecent }});
    
});

/*jQuery(document).ready(function(){
    jQuery('input.newMsgContent').focus();

    jQuery('.newChatForm').submit( function() {
        $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'html',
            data    : $(this).serialize(),
            error   : function() {
                console.debug("Failure sending new chat message");
            },
            success : function() {
                jQuery('input.newMsgContent').attr('value', '');
                jQuery('input.newMsgContent').focus();
                console.debug("Success sending chat message");
            }
        });
        return false;
    });

    jQuery('.spinner')
        .hide()  // hide it initially
        .ajaxStart(function() {
            $(this).show();
        })
        .ajaxStop(function() {
            $(this).hide();
        });
        });*/