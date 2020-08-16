from django import template
from ..models import Board


register = template.Library()




@register.filter
def alphaMove():
	board = Board.objects.get(name="game")
	return board.name

@register.simple_tag
def testest1():
	return "Test1 : SUCCESS";
