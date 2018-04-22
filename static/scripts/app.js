var app = angular.module("myModule", ['ngCookies']);

app.controller('HomeCtrl', ['$http','$scope','$cookies',function($http,$scope,$cookies) {

    // get data from flask
    $scope.callData = function($event){
        $event.preventDefault();
        $scope.hasSearch = 1;
        $scope.companies = {};     
        $http({
            method:'POST',
            url:'http://127.0.0.1:5000/iws/api/v1.0/companies',
            headers: {
               'Content-Type': 'application/json;charset=utf-8'
            },
            data: {'search':$scope.searchText,'page':$scope.currentPage}
        })
        .then(function(resp){
            $scope.companies = resp.data.data;
            $scope.totalCompanies = resp.data.total;
            $cookies.put('cookie', $scope.searchText)
        },function(error){
            console.log(error);
        });
    }

    // check cookie
    $scope.checkCookie = function(){
        $scope.currentPage = 0;
        $scope.hasSearch = 0;
        if ($cookies.get('cookie'))
        {
            $scope.hasSearch = 1;
            $scope.searchText = $cookies.get('cookie');
               $http({
                method:'POST',
                url:'http://127.0.0.1:5000/iws/api/v1.0/companies',
                headers: {
                   'Content-Type': 'application/json;charset=utf-8'
                },
                data: {'search':$scope.searchText,'page':$scope.currentPage}
            })
            .then(function(resp){
                $scope.companies = resp.data.data;
                $scope.totalCompanies = resp.data.total;
            },function(error){
                console.log(error);
            });
        }       
    }

    // pagination handling
    $scope.nextPage = function($event){
        if ($scope.currentPage < $scope.totalCompanies/20)
        {
            $scope.currentPage++;
            $scope.callData($event);
        }        
    }

    $scope.prevPage = function($event){
        if ($scope.currentPage > 0)
        {
            $scope.currentPage--;
            $scope.callData($event);
        }        
    }
}]);


// use fallback img if needed
app.directive('fallbackSrc', function () {
    var fallbackSrc = {
        link: function postLink(scope, iElement, iAttrs) {
            iElement.bind('error', function() {
                angular.element(this).attr("src", iAttrs.fallbackSrc);
            });
        }
    }
    return fallbackSrc;
});
