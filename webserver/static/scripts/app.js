var app = angular.module("myModule", ['ngCookies']);

app.controller('HomeCtrl', ['$http','$scope','$cookies',function($http,$scope,$cookies) {
    $scope.callData = function($event){
        $event.preventDefault();

        $scope.companies = {};
        console.log($scope.currentPage);        
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

    $scope.checkCookie = function(){
        $scope.currentPage = 0;
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

    $scope.getDomainUrl = function(url){
        $http.get('/api/myRemoteSiteTester', {params: {target: myUrl}}) 
           .success(function(data) {
                  alert(data);
            });
        return splitted[1];
    }
}]);

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
