var app = angular.module('TexasFyre', ['ngRoute', 'ui.bootstrap'])

app.config(function ($routeProvider){
	
	$routeProvider
		.when('/home', {
			templateUrl: 'views/home.html',
			controller: 'HomeController'
		})
		.when('/about', {
			templateUrl: 'views/about.html',
			controller: 'AboutController'
		})
		.when('/events', {
			templateUrl: 'views/events.html',
			controller: 'EventsController'
		})
		.when('/contact', {
			templateUrl: 'views/contact.html',
			controller: 'ContactController'
		});
})