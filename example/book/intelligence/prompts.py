from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.llm import Prompt
from example.book.intelligence.character.prompts import characters_intel_prompt
from example.book.intelligence.plot.prompts import plot_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


def book_intel_prompt(book_intel: BookIntel) -> Prompt:
    prompt = Prompt()
    
    if book_intel.start:
        prompt.text(f'Title: {book_intel.start.title}')
        prompt.text(f'Overview: {book_intel.start.overview}')
        prompt.line_break()

    if book_intel.world:

        prompt.text('World:')
        prompt.text(f'Name: {book_intel.world.name}')
        prompt.text(f'Description: {book_intel.world.description}')
        
        prompt.line_break()
        
        prompt.text(f'Locations: ')
        for location_intel in book_intel.world.locations:
            prompt.line_break()
            
            prompt.text(f'Name: {location_intel.name}')
            prompt.text(f'Description: {location_intel.description}')
            
        prompt.line_break()

    if book_intel.characters:
        prompt.prompt(characters_intel_prompt(book_intel.characters))

        prompt.line_break()
        
    if book_intel.plot:
        prompt.prompt(plot_intel_prompt(book_intel.plot))



    return prompt