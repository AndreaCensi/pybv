import progressbar

def create_progress_bar(job_id, total_iterations):
    widgets = [job_id, ' ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()), ' ', progressbar.ETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_iterations).start()
    return pbar
    
