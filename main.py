"""
  (c) Jonathan Shulgach - Cite and Notice license:
    All modifications to this code or use of it must include this notice and give credit for use.
    Credit requirements:
      All publications using this code must cite all contributors to this code.
      A list must be updated below indicating the contributors alongside the original or modified code appropriately.
      All code built on this code must retain this notice. All projects incorporating this code must retain this license text alongside the original or modified code.
      All projects incorporating this code must retain the existing citation and license text in each code file and modify it to include all contributors.
      Web, video, or other presentation materials must give credit for the contributors to this code, if it contributes to the subject presented.
      All modifications to this code or other associated documentation must retain this notice or a modified version which may only involve updating the contributor list.

    Primary Authors:
      - Jonathan Shulgach, PhD Student - Neuromechatronics Lab, Carnegie Mellon University

   Other than the above, this code may be used for any purpose and no financial or other compensation is required.
   Contributors do not relinquish their copyright(s) to this software by virtue of offering this license.
   Any modifications to the license require permission of the authors.

   Description:
      A simple asyncronous TCP web server that handles client commands to send to a connected robot via Serial USB
"""


from robot_server import AsyncServer

if __name__ == "__main__":
    try:
        server = AsyncServer(ip='192.168.1.157', port=5000)
        server.start()

    except KeyboardInterrupt:
        server.stop()

    finally:
        pass



