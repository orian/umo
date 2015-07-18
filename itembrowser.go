package main

import (
	"crypto/sha1"
	"encoding/json"
	"flag"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"path"
	"sort"

	"github.com/gorilla/mux"
	"github.com/orian/params"
)

func MainHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "you are here: %s", req.URL.String())
}

type FileData struct {
	Url      string
	Path     string
	Filename string
	Checksum string
}

type Item struct {
	Name     string
	FileUrls []string
	Files    []FileData
	Text     string
	Url      string
	Ref      string
	Order    int
}

type ItemType int

const (
	TypeNode (ItemType) = 1
	TypeFile (ItemType) = 2
)

type BrowseItem struct {
	Item
	ID       int
	Type     ItemType
	Parent   *BrowseItem
	Linked   []*BrowseItem // links
	Attached []*BrowseItem // files
}
type ItemBrowser struct {
	itemsByID map[int]*BrowseItem
	rootItems []*BrowseItem
	dataDir   string
}

func GetItemType(i *Item) ItemType {
	if len(i.Files) > 0 {
		return TypeFile
	}
	return TypeNode
}

// ByAge implements sort.Interface for []Person based on
// the Age field.
type ByOrder []*BrowseItem

func (a ByOrder) Len() int           { return len(a) }
func (a ByOrder) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByOrder) Less(i, j int) bool { return a[i].Order < a[j].Order }

func NewItemBrowser(file, data string) *ItemBrowser {
	configFile, err := os.Open(file)
	if err != nil {
		log.Fatalf("opening config file: %s", err.Error())
	}

	if fi, err := os.Stat(data); err != nil || !fi.IsDir() {
		log.Fatalf("%q is not a directory", data)
	}

	jsonParser := json.NewDecoder(configFile)
	var items []Item
	if err = jsonParser.Decode(&items); err != nil {
		log.Fatalf("parsing config file: %s", err.Error())
	}
	ib := &ItemBrowser{make(map[int]*BrowseItem), make([]*BrowseItem, 0), data}
	// create graph
	byUrl := make(map[string]*BrowseItem)
	for i, v := range items {
		bi := &BrowseItem{}
		bi.Item = v
		bi.ID = i + 1
		bi.Type = GetItemType(&v)
		byUrl[v.Url] = bi
		ib.itemsByID[bi.ID] = bi
	}
	for _, bi := range byUrl {
		if parent, ok := byUrl[bi.Ref]; ok {
			bi.Parent = parent
			switch bi.Type {
			case TypeNode:
				parent.Linked = append(parent.Linked, bi)
			case TypeFile:
				parent.Attached = append(parent.Attached, bi)
			}
		} else { // no parent
			ib.rootItems = append(ib.rootItems, bi)
		}
	}
	for _, bi := range ib.itemsByID {
		sort.Sort(ByOrder(bi.Linked))
		sort.Sort(ByOrder(bi.Attached))
	}
	return ib
}

func (ib *ItemBrowser) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "jestes tu: %s")
}

const detailTmplT = `<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>The HTML5 Herald</title>
  <meta name="description" content="The HTML5 Herald">
  <meta name="author" content="SitePoint">

  <link rel="stylesheet" href="css/styles.css?v=1.0">

  <!--[if lt IE 9]>
  <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
  <![endif]-->
</head>

<body>
  <script src="js/scripts.js"></script>
  <a href="/">Main</a>
  {{with .Parent}}<a href="/node/{{.ID}}">Parent</a>{{end}}

  <div>
  {{.Text}} {{.Url}}
  {{if .Files}}<a href="/download/{{.ID}}">download</a>{{end}}
  <p>
  Linkuje do:
  {{with .Linked}}
  <ul>
  {{range .}}
    <li>[{{.Order}}] {{.Text}} <a href="/node/{{.ID}}">details</a></li>
  {{end}}
  </ul>
  {{else}}brak{{end}}
  </p>

  <p>
  Pliki:
  {{with .Attached}}
  <ul>
  {{range .}}
    <li>[{{.Order}}] {{.Text}} <a href="/node/{{.ID}}">details</a></li>
  {{end}}
  </ul>
  {{else}}brak{{end}}
  </p>
  </div>
</body>
</html>`

var detailTmpl = template.Must(template.New("detail").Parse(detailTmplT))

func (ib *ItemBrowser) NodeHandler(w http.ResponseWriter, req *http.Request) {
	prms := params.NewParams(mux.Vars(req))
	id := prms.Get("id").Int()
	bi, ok := ib.itemsByID[id]
	if !ok {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	if err := detailTmpl.Execute(w, bi); err != nil {
		log.Printf("%+v", bi)
		log.Print(err)
	}
}

func (ib *ItemBrowser) FileHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "file: %s")
}

const listTmplT = `<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>The HTML5 Herald</title>
  <meta name="description" content="The HTML5 Herald">
  <meta name="author" content="SitePoint">

  <link rel="stylesheet" href="css/styles.css?v=1.0">

  <!--[if lt IE 9]>
  <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
  <![endif]-->
</head>

<body>
  <script src="js/scripts.js"></script>
  Wszystkie strony początkowe (entry points)
  <ul>
  {{range .}}
    <li>{{.Text}} - {{.Url}} <a href="/node/{{.ID}}">details</a></li>
  {{end}}
  </ul>
</body>
</html>`

var listTmpl = template.Must(template.New("list").Parse(listTmplT))

func (ib *ItemBrowser) MainHandler(w http.ResponseWriter, req *http.Request) {
	listTmpl.Execute(w, ib.rootItems)
}

func UrlToFilename(u string) string {
	h := sha1.New()
	io.WriteString(h, u)
	return fmt.Sprintf("%x", string(h.Sum(nil)))
}

func (ib *ItemBrowser) DownloadHandler(w http.ResponseWriter, req *http.Request) {
	prms := params.NewParams(mux.Vars(req))
	id := prms.Get("id").Int()
	bi, ok := ib.itemsByID[id]
	if !ok {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	if bi.Type != TypeFile || len(bi.Files) == 0 {
		http.Error(w, "not a file", http.StatusNotFound)
		return
	}
	if len(bi.Files[0].Filename) > 0 {
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%q", bi.Files[0].Filename))
	}
	f, err := os.Open(path.Join(ib.dataDir, UrlToFilename(bi.Files[0].Url)))
	if err != nil {
		log.Printf("content for metadata not found: %s", err)
		http.Error(w, "content not found", http.StatusInternalServerError)
		return
	}
	if d, err := io.Copy(w, f); err != nil {
		log.Printf("Could not copy file to response, copied: %d bytes", d)
		http.Error(w, "could not send?", http.StatusInternalServerError)
		return
	}
}

func main() {
	FLAG_file := flag.String("file", "", "an json file")
	FLAG_data := flag.String("data", "", "a directory where files are located")
	flag.Parse()

	log.Printf("reading: %s", *FLAG_file)
	log.Printf("files will be looked up in: %s", *FLAG_data)
	ib := NewItemBrowser(*FLAG_file, *FLAG_data)

	r := mux.NewRouter()
	r.HandleFunc("/node/{id}", ib.NodeHandler)
	r.HandleFunc("/node/{id}/file/{fileId}", ib.FileHandler)
	r.HandleFunc("/download/{id}", ib.DownloadHandler)
	r.HandleFunc("/", ib.MainHandler)
	http.Handle("/", r)
	log.Println(http.ListenAndServe(":8080", nil))
}
