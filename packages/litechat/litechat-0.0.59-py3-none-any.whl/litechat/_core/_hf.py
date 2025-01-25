# _hf.py
import asyncio
import json
import random
import sys
import time
from datetime import datetime
from typing import Literal, Optional, Dict, List

from loguru import logger

from ._utils import json_tag

logger.remove()
logger.add(sys.stderr, level='CRITICAL')
from litechat.types.hf_models import HFChatModels
from litechat._core._prompts import JSON_SYSTEM_PROMPT


class HuggingFaceAutomation:
    def __init__(self, browser_session):
        self.session = browser_session
        self.page = browser_session.page
        self.prev_conv_id: str = ""
        self._model: Optional[str] = None
        self._system_prompt: Optional[str] = None
        self._web_search: Optional[bool] = None

    @property
    def model(self) -> Optional[str]:
        return self._model

    @model.setter
    def model(self, value: Optional[str]):
        self._model = value

    @property
    def system_prompt(self) -> Optional[str]:
        return self._system_prompt

    async def set_system_prompt(self, value: Optional[str]):
        await self.write_system_prompt(value, force=True)

    async def set_model(self, value: Optional[str]):
        await self.update_model(value)

    async def set_web_search(self, value: Optional[bool]):
        await self.toggle_web_search(value)

    @property
    def web_search(self) -> Optional[bool]:
        return self._web_search

    async def generate(self, query: str, system_prompt: str = "", web_search: bool = False,
                       max_wait_time: int = 300,
                       conversation_id: str = "",
                       model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
                       ) -> str:
        async for chunk in self.stream_query(query, web_search, max_wait_time,
                                             system_prompt=system_prompt,
                                             conversation_id=conversation_id,
                                             model=model):
            yield chunk

    async def complete(self, query: str, system_prompt: str = "", web_search: bool = False,
                       max_wait_time: int = 300,
                       conversation_id: str = "",
                       model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                       response_format=None,
                       **kwargs
                       ) -> str:
        return await self.non_stream_query(query, web_search, max_wait_time,
                                           system_prompt=system_prompt,
                                           conversation_id=conversation_id,
                                           model=model,
                                           response_format=response_format,**kwargs)

    async def toogle_int_ws_button(self):
        try:
            search_button = self.page.locator('button.base-tool.svelte-10z3gx0').first
            if await search_button.is_visible():
                await search_button.click()
                await asyncio.sleep(1)
            else:
                search_area = self.page.locator('div.group/tooltip.inline-block.md:relative').first
                if await search_area.is_visible():
                    await search_area.click()
                    await asyncio.sleep(1)
        except Exception as e:
            raise Exception(f"Warning: Could not toggle web search: {e}")

    async def toggle_web_search(self, web_search: Optional[bool]):
        """
        _web_search ( previously)
        _current_web_search():

        if
        """
        if self._web_search is None:
            self._web_search = web_search
            if self._web_search:
                await self.toogle_int_ws_button()
        else:
            if self._web_search is True:
                if web_search is False:
                    await self.toogle_int_ws_button()
                    self._web_search = False
            else:
                if web_search:
                    await self.toogle_int_ws_button()
                    self._web_search = True

    async def write_and_chat(self, query, web_search):
        await self.toggle_web_search(web_search)
        textarea = self.page.locator('textarea')
        await textarea.fill(query)
        await textarea.press('Enter')



    async def write_system_prompt(self, prompt: str, force: bool = False,response_format=None) -> None:
        """Set the system prompt in the settings textarea."""
        prompt = prompt + (JSON_SYSTEM_PROMPT.format(schema=response_format) if response_format is not None else "")

        if force is False and (self._system_prompt == prompt):
            return

        self._system_prompt = prompt


        logger.debug("Setting system prompt")
        settings_selectors = [
            'a[aria-label="Settings"]',
            'button[aria-label="Settings"]',
            '.btn.ml-auto.flex.h-7.w-7.self-start.rounded-full',  # Based on the screenshot
            '[class*="settings"]'
        ]

        settings_button = None
        for selector in settings_selectors:
            try:
                settings_button = self.page.locator(selector).first
                if await settings_button.is_visible(timeout=2000):
                    logger.debug(f"Found settings button: {selector}")
                    break
            except Exception:
                continue

        if not settings_button:
            raise Exception("Could not find settings button")

        await settings_button.click()
        await asyncio.sleep(1)  # Wait for modal animation

        # Try multiple possible selectors for the system prompt textarea
        textarea_selectors = [
            'textarea[aria-label="Custom system prompt"]',
            'textarea[placeholder*="system prompt"]',
            'textarea[class*="system-prompt"]'
        ]

        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = self.page.locator(selector)
                if await textarea.is_visible(timeout=2000):
                    logger.debug(f"Found system prompt textarea: {selector}")
                    break
            except Exception:
                continue

        if not textarea:
            raise Exception("Could not find system prompt textarea")

        await textarea.fill(prompt)
        # await asyncio.sleep(2)

        # await self.page.mouse.click(10, 10)
        # try:
        #     new_chat_button = self.page.get_by_role("button", name="New Chat")
        #     try:
        #         await new_chat_button.wait_for(state="visible", timeout=5000)
        #         await new_chat_button.click()
        #     except Exception as e:
        #         try:
        #             await new_chat_button.click(force=True)
        #         except Exception as e2:
        #             logger.debug(f"Force click failed: {e2}")
        # except Exception as e:
        #     logger.debug(f"Failed to handle new chat button: {e}")
        # await asyncio.sleep(1)
        # logger.info(f"System prompt set successfully: {prompt[:50]}...")
        # Try to find and click the close button using various selectors
        close_button_selectors = [
            'button[aria-label="Close settings"]',
            'button.btn.rounded-lg[aria-label*="Close"]',
            'button[class*="rounded-lg"][aria-label*="Close"]',
            # SVG path selector as fallback
            'svg path[d*="M17.414 16L24 9.414L22.586 8L16 14.586L9.414 8L8 9.414L14.586 16L8 22.586L9.414 24L16 17.414L22.586 24L24 22.586"]'
        ]

        close_button = None
        for selector in close_button_selectors:
            try:
                close_button = self.page.locator(selector).first
                if await close_button.is_visible(timeout=2000):
                    logger.debug(f"Found close button: {selector}")
                    break
            except Exception:
                continue

        if close_button:
            try:
                await close_button.click()
                await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"Failed to click close button: {e}")
                # Fallback to clicking the closest parent button if direct click fails
                try:
                    parent_button = close_button.locator("xpath=ancestor::button").first
                    await parent_button.click()
                    await asyncio.sleep(1)
                except Exception as e2:
                    logger.debug(f"Failed to click parent button: {e2}")
                    raise Exception("Could not close settings modal")
        else:
            raise Exception("Could not find close button")

        logger.info(f"System prompt set successfully: {prompt[:50]}...")

    async def update_model(self, model):
        if self._model is None or self._model != model:
            self._model = model
            self._system_prompt = None
            await self.click_models()
            logger.debug(f"Updating model to: {model}")
            await self.select_model(model)

    async def stream_query(self, query, web_search=False, max_wait_time=300, system_prompt="",
                           conversation_id: str = "",
                           model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                           response_format=None
                           ):
        logger.debug(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing query: {query[:50]}...")

        await self.update_model(model)

        """
        if current convid is empty:
            perform write system prompt and write_chat 
        else if current convid is not empty:
            if current convid is different from previous convid:
                perform write system prompt and write_chat 
            else if current convid is same as previous convid:
                only write_chat
        """
        if (self.prev_conv_id != conversation_id) or conversation_id == "":
            await self.click_new_chat()
            await self.write_system_prompt(system_prompt)

        self.prev_conv_id = conversation_id

        await self.write_and_chat(query, web_search=web_search)

        min_chat_start_time = 1 + (7 if web_search else 0)
        await asyncio.sleep(min_chat_start_time)

        async for chunk in self.stream_text_logic(web_search=web_search, max_wait_time=max_wait_time):
            yield chunk

    async def non_stream_query(self, query, web_search=False, max_wait_time=300, system_prompt="",
                               conversation_id: str = "",
                               model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                               response_format=None,**kwargs
                               ):
        logger.debug(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing query: {query[:50]}...")

        stop:List = kwargs.get("stop",[])

        await self.update_model(model)

        """
        if current convid is empty:
            perform write system prompt and write_chat 
        else if current convid is not empty:
            if current convid is different from previous convid:
                perform write system prompt and write_chat 
            else if current convid is same as previous convid:
                only write_chat
        """
        if (self.prev_conv_id != conversation_id) or conversation_id == "":
            await self.click_new_chat()
            await self.write_system_prompt(prompt=system_prompt,response_format=response_format)

        self.prev_conv_id = conversation_id

        ## add JSON Dict for response if required
        query += json_tag(response_format)

        await self.write_and_chat(query, web_search=web_search)

        min_chat_start_time = 1 + (7 if web_search else 0)
        await asyncio.sleep(min_chat_start_time)

        unchanged_count = 0
        start_time = time.time()
        last_length = 0  # Track the last length instead of storing full previous text

        while True:
            try:
                response_element = self.page.locator('.prose').last
                current_text = await response_element.inner_text()



                if not current_text:
                    await asyncio.sleep(0.5)
                    continue

                if stop and any(s in current_text for s in stop):
                    idx = [s in current_text for s in stop].index(True)
                    return self.process_response(current_text.split(stop[idx])[0])

                current_length = len(current_text)

                # Check if response is complete (no changes in last 2 checks)
                if current_length == last_length:
                    unchanged_count += 1
                    if unchanged_count >= 2:
                        logger.debug(f'Stopping reason unchanged_count: {unchanged_count}')
                        return self.process_response(current_text)
                else:
                    unchanged_count = 0

                last_length = current_length

                if time.time() - start_time >= max_wait_time:
                    return self.process_response(current_text)

                await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"Error while monitoring response: {e}")
                return ""

    async def stream_text_logic(self, web_search=False, max_wait_time=300):
        unchanged_count = 0
        start_time = time.time()
        last_length = 0  # Track the last length instead of storing full previous text

        while True:
            try:
                response_element = self.page.locator('.prose').last
                current_text = await response_element.inner_text()

                if not current_text:
                    await asyncio.sleep(0.5)
                    continue

                current_length = len(current_text)

                if current_length > last_length:
                    new_content = current_text[last_length:]
                    yield new_content

                # Check if response is complete (no changes in last 2 checks)
                if current_length == last_length:
                    unchanged_count += 1
                    if unchanged_count >= 2:
                        logger.debug(f'Stopping reason unchanged_count: {unchanged_count}')
                        break
                else:
                    unchanged_count = 0

                last_length = current_length

                if time.time() - start_time >= max_wait_time:
                    break

                await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"Error while monitoring response: {e}")
                break

    async def click_new_chat(self):
        try:
            new_chat_button = self.page.get_by_role("link", name="New Chat").first
            try:
                await new_chat_button.wait_for(state="visible", timeout=5000)
                await new_chat_button.click()
                await asyncio.sleep(1)
            except Exception as e:
                try:
                    await new_chat_button.click(force=True)
                    await asyncio.sleep(1)
                except Exception as e2:
                    logger.debug(f"Force click failed: {e2}")
        except Exception as e:
            logger.debug(f"Failed to handle new chat button: {e}")

    async def click_models(self):
        try:
            new_chat_button = self.page.get_by_role("link", name="Models").first
            await new_chat_button.wait_for(state="visible", timeout=5000)
            await new_chat_button.click()
            await asyncio.sleep(2)
        except Exception as e:
            logger.debug(f"Failed to handle new chat button: {e}")

    async def select_model(self, model):
        try:
            new_chat_button = self.page.get_by_role("link", name=model).first
            await new_chat_button.wait_for(state="visible", timeout=5000)
            await new_chat_button.click()
            await asyncio.sleep(2)
        except Exception as e:
            logger.debug(f"Failed to handle new chat button: {e}")

    def process_response(self, current_text):
        if 'Copied' in current_text:
            return current_text.split('Copied')[0].strip()
        else:
            return current_text