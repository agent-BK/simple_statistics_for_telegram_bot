# simple_statistics_for_telegram_bot

**Simple statistics of telegram bots 1.0** 
Author: Andrey Voitovich
For the development of other functions, troubleshooting and issues related to the development, please contact by e-mail: [agent@bk.ru](mailto:agent@bk.ru)

**Available commands:**

***Get statistics:***
 - shows statistics for the selected time period.
 - statistics on the number of days starting from the current day are
   displayed.
 - statistics on the number of users and the number of commands entered
   are available.
 - statistics are cleared automatically after 30 days.
 - statistics can be uploaded to the screen and to a txt file

***Clear all statistics:***
 - forced clearing of all statistics.

***Using a csv table instead of DB, with telebot***

**Connection:**

     import modules.analytic_telegramm_bot.analytic as analytic

**calling statistics**

	def text_processing(message):
		mes_id = message.from_user.id
		message_user = message.text

		# keywords for entering statistics
		admin_dict = ['\options', '\настройки']

		# id of the bot owner to access statistics
		admin_id = 0000001

		if (message_user in admin_dict) and (mes_id == admin_id):
			# password for accessing statistics
			password = 'we come up with a password to log in to statistics'
			# calling statistics
			analytic.get_statistics(message, bot, markup_remove, password)
		else:
			bot.send_message(mes_id, text=text_translate[0])
			counting statistics
			analytic.statistics(mes_id, 'text')

**statistics**

     analytic.statistics(mes_id, message.text)

***

**Простая статистика телеграм ботов 1.0** 
Автор: Андрей Войтович
По вопросам разработки других функций, устранения ошибок и вопросов связанных с разработкой обращаться по e-mail: [agent@bk.ru](mailto:agent@bk.ru)

**Доступные команды:**

**Получить статистику:**
- показывает статистику за выбранный переод времени.
- отображается статистика по количеству дней начиная от текущего дня.
- доступна статистика по количеству пользователей и количеству введенных команд.
- очистка статистики происходит автоматически по прошествию 30 дней.
- выгрузка статистики возможна на экран и в txt файл

**Очистить всю статистику:**
- принудительная очистка всей статистики.

**C использованием вместо ДБ csv таблицы, с telebot** 


**подключение**

    import modules.analytic_telegramm_bot.analytic as analytic

**вызов статистики**

	def text_processing(message):
		mes_id = message.from_user.id
		message_user = message.text

		# ключевое слова для входа в статистику
		admin_dict = ['\options', '\настройки']

		# id владельца бота для доступа к статистике
		admin_id = 0000001

		if (message_user in admin_dict) and (mes_id == admin_id):
			# пароль доступа к статистике
			password = 'придумываем пароль для входа в статистику'
			# вызов статистики
			analytic.get_statistics(message, bot, markup_remove, password)
		else:
			bot.send_message(mes_id, text=text_translate[0])
			#подсчет статистики
			analytic.statistics(mes_id, 'текст')

**подсчет статистики**

    analytic.statistics(mes_id, message.text)
