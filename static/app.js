

class TripView {
    
    mainView(){

    }   
}

class ComponentBuilder {
    constructor(name, field, searchTerm){
        this.name = name
        this.field = field
        this.searchTerm = searchTerm
    }
    fieldToAPI_Button(name, field){
        submitFunction(name, field)
        function submitFunction(name, field) {
            if (field == "searchpoi"){
                let fieldValue = document.getElementById(field)
                let submitButton = document.getElementById(name)
                submitButton.addEventListener("click", (e)=> {
                    e.preventDefault()
                    sessionStorage.clear()
                    let mainView = document.getElementById('main_view_js_1')
                    //console.log(mainView)
                    mainView.innerHTML = ""
                    submitToFlask(fieldValue.value)
                })
            }
            else {
            
                    //console.log(name)
                    let buttonCard = document.getElementById(name)
                    let findMoreButtons = buttonCard.getElementsByClassName("find-more")
                    let saveButtons = buttonCard.getElementsByClassName("save-card")
                    for (let button of findMoreButtons){
                        button.addEventListener("click", (e)=>{
                            e.preventDefault()
                            submitToFlask(field)
                        })
                    }
                    for (let button of saveButtons){
                        button.addEventListener("click", (e)=>{
                            e.preventDefault()
                            submitToFlask(button)
                        })   
                    }

                }
        }

        async function submitToFlask(searchTerm=null){
            if (searchTerm.id == "save"){
                let card = document.getElementById(searchTerm.name)
                console.log(card)
                if (card.querySelector("img")){
                    let imageUrl = card.querySelector("img").src
                    let cardTitle = card.getElementsByClassName('card-title')[0].innerHTML
                    let cardText = card.getElementsByClassName('card-text')[0].innerHTML
                    let cardId = searchTerm.name
                    console.log("image")
                    const response = await axios({
                        method: 'post',
                        url: `/api/${cardId}`,
                        params:{
                            imageUrl: imageUrl,
                            cardTitle:  cardTitle,
                            cardText: cardText,
                            cardId: cardId
                        }
                    })
                    console.log(response)

                }
                else{
                    console.log("none")
                    let cardTitle = card.getElementsByClassName('card-title')[0].innerHTML
                    let cardText = card.getElementsByClassName('card-text')[0].innerHTML
                    let cardId = searchTerm.name
                    const response = await axios({
                        method: 'post',
                        url: `/api/${cardId}`,
                        params:{
                            cardTitle: cardTitle,
                            cardText: cardText,
                            cardId: cardId
                        }
                    })
                    console.log(response)

                }



            }
            else if (searchTerm){
                console.log(searchTerm.id)
                const response = await axios({
                    method: 'post',
                    url: '/api',
                    params: {
                        searchTerm: searchTerm
                    }
                })
                sessionStorage.setItem("response", JSON.stringify(response))
                write()
            }

            else{
                console.log(searchTerm[0])

                const response = await axios({
                    method: 'post',
                    url: '/api',
                    params:{
                        searchTerm: "mke"
                    }
                })
                console.log("mke")
            }

        }
        function write(){
            let tm = JSON.parse(sessionStorage.getItem("response"))
            let dataCatch = document.createElement("div")
            dataCatch.innerHTML = tm.data
            let forms = dataCatch.querySelectorAll("FORM")
            for (let form of forms){
                //console.log(form.id)
                let title = form.getElementsByClassName("card-title")
                title = title[0]["innerHTML"]
                let mainView = document.getElementById('main_view_js_1')
                if (sessionStorage.getItem("idStorage")){
                    let idStorage = JSON.parse(sessionStorage.getItem("idStorage"))
                    let matchFound = false
                    for (let id of idStorage){
                        if (id === form.id){
                            matchFound = true
                            break
                        }
                    }
                    if (matchFound === false){
                        idStorage.push(form.id)
                        sessionStorage.setItem("idStorage", JSON.stringify(idStorage))
                        mainView.prepend(form)
                        //form.insertBefore(document.createElement("p"), mainView.firstChild)
                        submitFunction(form.id, title)
                    }
                }
                else {
                    let idStorage = []
                    idStorage.push(form.id)
                    mainView.prepend(form)
                
                    submitFunction(form.id, title)
                    sessionStorage.setItem("idStorage", JSON.stringify(idStorage))

                }


            

            }

        }
    }
}




function siteMaker(){
    const start = new TripView()
    start.mainView()
    const searchControls = new ComponentBuilder()
    searchControls.fieldToAPI_Button("submitpoi", "searchpoi")

}

siteMaker()