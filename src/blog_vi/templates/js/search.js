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

function findAndReplaceString(str, find) {
  var reg = new RegExp('(' + find + ')', 'gi');
  return str.replace(reg, '<mark>$1</mark>');
}

document.addEventListener("DOMContentLoaded", function (event) {
  document.getElementById('search').addEventListener("keyup", function () {
    let searchValue = this.value.trim();
    let search_field_options;
    if (searchValue !== '') {
      getJSON('data.json', function (error, result) {

        var list = result;
        if (error) {
          console.log(error);
          return;
        }
        search_field_options = window['searchConfig'];
        // console.log(search_field_options)
        let options = {
          keys: [
            {
              name: 'title',
              weight: 8
            },
            {
              name: 'summary',
              weight: 6
            },
            {
              name: 'author_name',
              weight: 5
            },
            {
              name: 'categories',
              weight: 3
            }
          ]
        };

        // console.log(search_field_options.keys.length)
        if (search_field_options.keys.length > 0) {
          options = search_field_options
        }
        var fuse = new Fuse(list, options);
        var searchResult = fuse.search(searchValue);
        let searchBar = document.getElementById("search-bar");
        searchBar.style.display = "block";
        let ulBar = searchBar.querySelector('ul');
        ulBar.innerHTML = '';
        ulBar.innerHTML = ulBar.innerHTML + '<li class="block px-4 pb-2 text-sm text-gray-700 font-bold border-b">Search results (' + Math.min(searchResult.length, 5) + '/' + searchResult.length + '):</li>';
        if (searchResult.length > 0) {
          for (let i = 0; i < Math.min(searchResult.length, 5); i++) {
            var blog = searchResult[i];
            ulBar.innerHTML = ulBar.innerHTML +
              '<li class="block cursor-pointer px-4 py-2 text-sm text-gray-700 border-b hover:bg-gray-100">' +
              '<a href="blogs/' + blog.item.detail_url + '">' +
              '<p class="mb-1 font-semibold">' +
              findAndReplaceString(blog.item.title, searchValue) +
              ' </p>' +
              '<p class="text-xs mb-1">' +
              findAndReplaceString(blog.item.summary, searchValue).split(" ").splice(0, 15).join(" ") +
              '</p>' +
              '<p class="mb-2 font-bold" ' +
              findAndReplaceString(blog.item.author_name, searchValue) +
              '</p>'
            '</a>' +
            '</li>';
          }
        } else {
          ulBar.innerHTML = ulBar.innerHTML + '<li class="block cursor-pointer px-4 py-2 text-sm text-gray-700 border-b hover:bg-gray-100">' +
            '<p class="mb-1 font-semibold">' +
            'No such content' +
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

