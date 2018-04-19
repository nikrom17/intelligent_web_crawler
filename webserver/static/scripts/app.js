var app = angular.module("myModule", ['ngCookies']);

app.controller('HomeCtrl', ['$http','$scope','$cookies',function($http,$scope,$cookies) {
    $scope.callData = function($event){
        $event.preventDefault();

        $scope.companies = {};
        $http({
            method:'POST',
            url:'http://127.0.0.1:5000/iws/api/v1.0/companies',
            headers: {
               'Content-Type': 'application/json;charset=utf-8'
            },
            data: {'search':$scope.searchText}
        })
        .then(function(resp){
            $scope.companies = resp.data.companies.values;
            $cookies.put('cookie', $scope.searchText)
        },function(error){
            console.log(error);
        });
    }

    $scope.checkCookie = function(){
        if ($cookies.get('cookie'))
        {
           $scope.searchText = $cookies.get('cookie');
           console.log("hascookie");
               $http({
                method:'POST',
                url:'http://127.0.0.1:5000/iws/api/v1.0/companies',
                headers: {
                   'Content-Type': 'application/json;charset=utf-8'
                },
                data: {'search':$cookies.get('cookie')}
            })
            .then(function(resp){
                $scope.companies = resp.data.companies.values;
            },function(error){
                console.log(error);
            });
        }       
    }
}]);