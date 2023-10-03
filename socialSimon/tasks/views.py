from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return JsonResponse({'success': True, 'task_id': task.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = TaskForm()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
            return render(request, 'tasks/partial_task_form.html', {'form': form})
        return render(request, 'tasks/create_task.html', {'form': form})
    
@login_required
def edit_task(request, task_id=None):  # <-- Include task_id parameter
    task = get_object_or_404(Task, id=task_id, user=request.user) if task_id else None
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return JsonResponse({'success': True, 'task_id': task.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = TaskForm(instance=task)  # <-- Use the instance parameter to preload task data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if it's an AJAX request
            return render(request, 'tasks/partial_task_form.html', {'form': form, 'task': task})
        return render(request, 'tasks/create_task.html', {'form': form})
    

@login_required
def delete_task(request, task_id=None):
    task = get_object_or_404(Task, id=task_id, user=request.user) if task_id else None
    if request.method == "DELETE":
        if task:  # Ensure the task exists
            task.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Task not found.'})
    else:
        # Handle other methods, e.g., GET
        # This can be any response, but for this example, let's return a simple message.
        return JsonResponse({'message': 'Use DELETE method to delete the task.'})
