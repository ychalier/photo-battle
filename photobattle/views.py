from pyexpat import model
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from . import models


def landing(request):
    return render(request, "photobattle/landing.html", {})


def view_battle(request, code):
    query = models.Battle.objects.filter(code=code)
    if not query.exists():
        raise Http404("Battle does not exist")
    battle = query.get()
    return render(request, "photobattle/battle.html", {
        "battle": battle,
        "is_owner": request.user == battle.owner,
        "imgbb_apikey": settings.PHOTOBATTLE_IMGBB_APIKEY,
    })


@permission_required("photobattle.change_battle")
def manage_battle(request, code):
    query = models.Battle.objects.filter(code=code)
    if not query.exists():
        raise Http404("Battle does not exist")
    battle = query.get()
    if not battle.owner == request.user:
        return redirect("photobattle:view_battle", code=battle.code)
    if request.method == "POST":
        if request.POST["action"] == "register_team":
            # TODO: filter/exists safe
            team = models.Team.objects.get(id=int(request.POST["team"]))
            battle.teams.add(team)
            battle.save()
        elif request.POST["action"] == "create_team":
            team_name = request.POST["team"].strip()
            if not models.Team.objects.filter(name=team_name).exists():
                models.Team.objects.create(name=team_name)
        elif request.POST["action"] == "remove_team":
            # TODO: filter/exists safe
            team = models.Team.objects.get(id=int(request.POST["team"]))
            battle.teams.remove(team)
            battle.save()
        elif request.POST["action"] == "change_state":
            if request.POST["state"] == models.Battle.STATE_CLOSED:
                # TODO: compute results
                photo_grades_details = dict()
                for vote in battle.votes.all():
                    split = vote.ranking.split(",")
                    for i, photo_id_str in enumerate(split):
                        photo_id = int(photo_id_str)
                        photo_grades_details.setdefault(photo_id, [0, 0])
                        photo_grades_details[photo_id][0] += i
                        photo_grades_details[photo_id][1] += len(split) - 1
                photo_grades = dict()
                for photo_id, (total_vote, total_max) in photo_grades_details.items():
                    if total_max == 0:
                        photo_grades[photo_id] = 0
                    else:
                        photo_grades[photo_id] = total_vote / total_max
                team_grades_details = dict()
                for photo in battle.photos.all():
                    team_grades_details.setdefault(photo.team.id, [0, 0])
                    team_grades_details[photo.team.id][0] += photo_grades.get(photo.id, 0)
                    team_grades_details[photo.team.id][1] += 1
                    photo.grade = photo_grades.get(photo.id, 0)
                    photo.save()
                team_grades = dict()
                for team_id, (total_vote, total_max) in team_grades_details.items():
                    if total_max == 0:
                        team_grades[team_id] = 0
                    else:
                        team_grades[team_id] = total_vote / total_max
                team_ranks = dict()
                for i, (team_id, team_grade) in enumerate(sorted(team_grades.items(), key=lambda x: -x[1])):
                    team_ranks[team_id] = i + 1
                # Delete previous results
                models.Result.objects.filter(battle=battle).delete()
                for team in battle.teams.all():
                    models.Result.objects.create(
                        battle=battle,
                        team=team,
                        rank=team_ranks.get(team.id, battle.teams.count()),
                        grade=team_grades.get(team.id, 0)
                    )
            battle.state = request.POST["state"]
            battle.save()
        elif request.POST["action"] == "delete_photo":
            # TODO: filter/exists safe
            photo = models.Photo.objects.get(id=int(request.POST["photo"]))
            photo.delete()
        elif request.POST["action"] == "delete_vote":
            # TODO: filter/exists safe
            vote = models.Vote.objects.get(id=int(request.POST["vote"]))
            vote.delete()
    next_state_value = None
    next_state_display = None
    for i in range(len(models.Battle.STATE_CHOICES) - 1):
        if models.Battle.STATE_CHOICES[i][0] == battle.state:
            next_state_value, next_state_display = models.Battle.STATE_CHOICES[i + 1]
            break
    return render(request, "photobattle/manage_battle.html", {
        "battle": battle,
        "teams": models.Team.objects.all(),
        "battle_states": models.Battle.STATE_CHOICES,
        "next_state_value": next_state_value,
        "next_state_display": next_state_display,
    })


@permission_required("photobattle.add_battle")
def view_profile(request):
    if request.method == "POST":
        if request.POST["action"] == "create_battle":
            battle = models.Battle.objects.create(
                owner=request.user,
                title=request.POST["title"],
                photo_count=int(request.POST["photo_count"])
            )
            return redirect("photobattle:manage_battle", code=battle.code)
        elif request.POST["action"] == "delete_battle":
            # TODO: filter/exists safe
            battle = models.Battle.objects.get(id=int(request.POST["battle"]))
            battle.delete()
    return render(request, "photobattle/profile.html", {
        "battles": models.Battle.objects.filter(owner=request.user)
    })


def api(request):
    response_status = 400
    response_success = False
    response_message = ""
    if request.method == "POST":
        if request.POST.get("action") == "upload_image":
            if models.Battle.objects.filter(id=int(request.POST["id"])).exists():
                battle = models.Battle.objects.get(id=int(request.POST["id"]))
                if battle.state == models.Battle.STATE_UPLOADING:
                    if models.Team.objects.filter(id=int(request.POST["team"])).exists():
                        team = models.Team.objects.get(id=int(request.POST["team"]))
                        if models.Photo.objects.filter(battle=battle, team=team).count() >= battle.photo_count:
                            response_message = "Maximum number of photos reached"
                        else:
                            models.Photo.objects.create(
                                battle=battle,
                                team=team,
                                url=request.POST["url"],
                                url_thumbnail=request.POST["url_thumbnail"],
                            )
                            response_status = 200
                            response_success = True
                    else:
                        response_message = "Incorrect team id"
                else:
                    response_message = "Battle state does not allow that"
            else:
                response_message = "Incorrect battle id"
        elif request.POST.get("action") == "send_vote":
            if models.Battle.objects.filter(id=int(request.POST["id"])).exists():
                battle = models.Battle.objects.get(id=int(request.POST["id"]))
                if battle.state == models.Battle.STATE_VOTING:
                    if models.Team.objects.filter(id=int(request.POST["team"])).exists():
                        team = models.Team.objects.get(id=int(request.POST["team"]))
                        models.Vote.objects.create(
                            battle=battle,
                            team=team,
                            ranking=request.POST["ranking"].strip()
                        )
                        response_status = 200
                        response_success = True
                    else:
                        response_message = "Incorrect team id"
                else:
                    response_message = "Battle state does not allow that"
            else:
                response_message = "Incorrect battle id"
        else:
            response_message = "Incorrect action"
    return JsonResponse(status=response_status, data={
        "success": response_success,
        "message": response_message
    })