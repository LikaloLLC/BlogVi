var getJSON = function (url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';

  xhr.onload = function () {

    var status = xhr.status;

    if (status === 200) {
      callback(null, xhr.response);
    } else {
      callback(status);
    }
  };

  xhr.send();
};
document.addEventListener("DOMContentLoaded", function (event) {
  document.getElementById('search').addEventListener("keyup", function () {
    let searchValue = this.value.trim();
    if (searchValue !== '') {
      getJSON('data.json', function (error, result) {
        var list = result;
        var weight = result.length;
        const options = {
          keys: [
            {
              name: "author_name"
            },
            {
              name: "categories",
              weight: weight
            },
            {
              name: "author_info"
            },
          ]
        };
        var fuse = new Fuse(list, options);
        var searchResult = fuse.search(searchValue);
        let searchBar = document.getElementById("search-bar");
        searchBar.style.display = "block";
        let ulBar = searchBar.querySelector('ul');
        ulBar.innerHTML = '';
        ulBar.innerHTML = ulBar.innerHTML + '<li class="block px-4 pb-2 text-sm text-gray-700 font-bold border-b">Search results (' + searchResult.length + '):</li>';
        if (searchResult.length > 0) {
          for (let i = 0; i < Math.min(searchResult.length, 5); i++) {
            var blog = searchResult[i];
            ulBar.innerHTML = ulBar.innerHTML +
              '<li class="block cursor-pointer px-4 py-2 text-sm text-gray-700 border-b hover:bg-gray-100">' +
              '<a href="blogs/'+blog.item.detail_url+'">'+
              '<p class="mb-1 font-semibold">' +
               blog.item.author_name.replaceAll(searchValue, '<mark>'+searchValue+'</mark>') +
              ' </p>' +
              '<p class="text-xs">' + blog.item.author_info + '</p>' +
              '</a>'+
              '</li>';

            console.log(blog);
          }
        } else {
          ulBar.innerHTML = ulBar.innerHTML + '<li class="block cursor-pointer px-4 py-2 text-sm text-gray-700 border-b hover:bg-gray-100">' +
            '<p class="mb-1 font-semibold">' +
            'No such contenet' +
            ' </p>' +
            '</li>';
          console.log("No such Content")
        }

      })
    } else {

        let searchBar = document.getElementById("search-bar");
        searchBar.style.display = "none";
    }
  })
})

