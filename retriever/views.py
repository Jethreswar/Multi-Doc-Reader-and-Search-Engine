from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Documents
from .forms import SearchForm
from django.conf import settings
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from .models import collection, QueryHistory
from .utils import get_positions, highlight_query_in_text, merge_lists, highlight_text_in_pdf
import os 
import fitz


@csrf_exempt
def upload_files(request):
    if request.method == "POST":
        files = request.FILES.getlist(
            "file"
        )  # memoryuploadfile object .. having name, content_type, size, charset, content, read, chunks, multiple_chunks
        urls = request.POST.getlist("links")
        urls = "".join(urls).split(",")
        for file in files:
            Documents(file=file).save()
        if urls[0] == "":
            urls = []
        for url in urls:
            Documents(url=url).save()
        context_data = {"show": True}
        return render(request, "retriever/upload_file.html", context=context_data)
    else:
        return render(request, "retriever/upload_file.html")


@csrf_exempt
def searchView(request):
    if request.method == "POST":
        # form = SearchForm(request.POST)
        all_instances = QueryHistory.objects.all()
        # if form.is_valid():
            # query = form.cleaned_data["query"]
            # query_list = query.split("|")
            # big_color_array = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'brown', 'black', 'white', 'gray', 'lightblue', 'lightgreen', 'lightyellow', 'lightpurple', 'lightorange', 'lightpink', 'lightcyan', 'lightmagenta', 'lightbrown', 'lightblack', 'lightwhite', 'lightgray']
            # color_array = big_color_array[:len(query_list)]

        instances = QueryHistory.objects.filter(checked = True)
        query_list = []
        color_array = []

        for instance in instances:
            query_list.append(instance.query)
            color_array.append(instance.color)
        print("color", color_array)

        processed_list = []
        for q in query_list:
            processed_list.append(get_positions(collection.find(), q))

        data = merge_lists(processed_list)
        for d in data:
            d["org_document"] = Documents.objects.get(id=d["id"])
            d["highlighted_content"] = highlight_query_in_text(
                (d["org_document"].text).replace("\n", "<br>"),
                query_list,
                color_array=color_array,
                tag_name="span",
                # style="color:red;background-color:yellow;",
            )
            for q in d['query']:
                q['color'] = color_array[query_list.index(q['query'])]

            # d['color'] = color_array[query_list.index(d['query'])]
            if d.get("extension") == "pdf":
                pdf_path = d['org_document'].file.path
                highlight_text_in_pdf(pdf_path, query_list, color_array, pdf_path.replace(".pdf", "_highlighted.pdf"))
                # print("pdf_path:", pdf_path)
                # doc = fitz.open(pdf_path)
                # for page in doc:
                #     text_instances = page.search_for(query)
                #     for inst in text_instances:
                #         highlight = page.add_highlight_annot(inst)
                #         highlight.set_colors(stroke=fitz.pdfcolor['pink'])
                #         highlight.update() 
                # highlight_path = pdf_path.replace(".pdf", "_highlighted.pdf")
                # doc.save(highlight_path)
                # doc.close()
            # d['highlighted_content'] = mark_safe((d['org_document'].text).replace(query, f"<span style='color:red;background-color:yellow;'>{query}</span>").replace("\n", "<br>").replace('"',''))
            # d['highlighted_content'] = re.sub(r"\b" + query + r"\b", lambda x: f"<span style='color:red;background-color:yellow;'>{x.group()}</span>", d['org_document'].text, flags=re.IGNORECASE)


        pdf_found_count = 0
        text_found_count = 0
        html_found_count = 0
        image_found_count = 0
        url_found_count = 0
        docx_found_count = 0
        ppt_found_count = 0

        for d in data:
            if d.get("extension") == "pdf":
                pdf_found_count += 1
            elif d.get("extension") == "txt":
                text_found_count += 1
            elif d.get("extension") == "html":
                html_found_count += 1
            elif d.get("extension") in ["png", "jpg", "jpeg", "gif", "bmp"]:
                image_found_count += 1
            elif d.get("extension") == "docx":
                    docx_found_count += 1
            elif d.get("extension") == "pptx":
                    ppt_found_count += 1
            else:
                url_found_count += 1

        context_data = {
            "instances": all_instances,
            "results": {
                "total_documents_found": len(data),
                "pdf_found": pdf_found_count,
                "text_found": text_found_count,
                "html_found": html_found_count,
                "image_found": image_found_count,
                "url_found": url_found_count,
                "total_documents": Documents.objects.all().count(),
                "docx_found": docx_found_count,
                "ppt_found": ppt_found_count,
                "data": data,
            },
        }
        return render(request, "retriever/search.html", context=context_data)
    if request.method == "GET":
        instances = QueryHistory.objects.order_by('id')
    return render(request, "retriever/search.html", {"instances": instances})


@csrf_exempt
def deleteDocumentView(request):
    if request.method == "POST":
        path = request.POST.get("path_redirect")
        print(request.POST)
        Documents.objects.all().delete()
        QueryHistory.objects.all().delete() 
        collection.delete_many({})
        dir_path = os.path.join((str(settings.MEDIA_ROOT)), 'documents')
        for file in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, file))
        # es.delete_by_query(index="my_document_index", body={"query": {"match_all": {}}})
        return HttpResponseRedirect(path)
    return HttpResponse("Invalid Request")


def ViewDocuments(request):
    documents = Documents.objects.all()

    context_data = {
        "documents": documents,
        "pdf_count": Documents.count_pdf(Documents),
        "text_count": Documents.count_text(Documents),
        "html_count": Documents.count_html(Documents),
        "image_count": Documents.count_image(Documents),
        "url_count": Documents.count_url(Documents),
        "docx_count": Documents.count_docx(Documents),  
        "ppt_count": Documents.count_ppt(Documents),
    }
    return render(request, "retriever/all_documents.html", context=context_data)


from django.http import JsonResponse
import json


@csrf_exempt 
def addQueryHistory(request):
    if request.method == 'POST':
        # Get the POST data
        post_data = json.loads(request.body)
        query = post_data.get('query', '')
        color = post_data.get('color', '')
        checked = post_data.get('checked', False)
        instance = QueryHistory.objects.create(query=query, color=color, checked=checked)
        response_data = { 
            'message': 'Query history added successfully',
            'data' : {
            'id' : instance.id,
            'query': instance.query,
            'color': instance.color,
            'checked': instance.checked,
            }
        }
        return JsonResponse(response_data)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Only POST requests are allowed'})
    


@csrf_exempt
def deleteQueryHistory(request):
    print("request", request.body)
    body = json.loads(request.body)
    print("body", body)
    query_id = body.get('query_id', '')
    try:
        instance = QueryHistory.objects.get(id=query_id)
    except QueryHistory.DoesNotExist:
        return JsonResponse({'error': 'Given query id does not exist in the database'},status = 404 )
    
    if request.method == 'DELETE':
        instance.delete()
        response_data = { 
            'message': 'Query history deleted successfully',
            'data' : {
                'id' : query_id,
                'query': instance.query,
                'color': instance.color,
                'checked': instance.checked,
            
            }
        }
        return JsonResponse(response_data)
    
    if request.method == 'PATCH':
        instance.checked = not instance.checked
        instance.save()
        response_data = { 
            'message': 'Query history updated successfully',
            'data' : {
                'id' : query_id,
                'query': instance.query,
                'color': instance.color,
                'checked': instance.checked,
            
            }
        }
        return JsonResponse(response_data)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Only POST requests are allowed'})